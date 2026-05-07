#include <float.h>
#include <math.h>
#include <stdint.h>

#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

#include "knn_model.h"

LOG_MODULE_REGISTER(main, LOG_LEVEL_INF);

#define IMU_SAMPLE_RATE_HZ 208
#define POLL_INTERVAL_MS 5
#define WINDOW_DURATION_MS 2000LL
#define MIN_WINDOW_SAMPLES 50
#define INACTIVITY_REMINDER_MS (10LL * 60LL * 1000LL)
#define HAPTIC_EFFECT 16
#define HAPTIC_DURATION_MS 1000
#define GRAVITY_MS2 9.80665f
#define GYRO_RAD_TO_DEG 57.2957795f

static const struct i2c_dt_spec dev_i2c = {
	.bus = DEVICE_DT_GET(DT_NODELABEL(i2c22)),
	.addr = 0x5A,
};

struct signal_stats {
	float sum;
	float sumsq;
	float min;
	float max;
};

struct window_stats {
	uint32_t count;
	struct signal_stats gyro_x;
	struct signal_stats gyro_mag;
	struct signal_stats accel_z;
	struct signal_stats acc_motion_mag;
};

static void drv_write(uint8_t reg, uint8_t val)
{
	uint8_t buf[2] = {reg, val};
	int ret = i2c_write_dt(&dev_i2c, buf, sizeof(buf));
	if (ret != 0) {
		LOG_ERR("DRV2605L I2C write failed: %d", ret);
	}
}

static void play_haptic_alert(void)
{
	drv_write(0x04, HAPTIC_EFFECT);
	k_msleep(10);
	drv_write(0x0C, 1);
	k_msleep(HAPTIC_DURATION_MS);
}

static inline float out_ev(const struct sensor_value *val)
{
	return val->val1 + (float)val->val2 / 1000000.0f;
}

static int set_sampling_freq(const struct device *dev)
{
	struct sensor_value odr_attr = {
		.val1 = IMU_SAMPLE_RATE_HZ,
		.val2 = 0,
	};

	int ret = sensor_attr_set(dev, SENSOR_CHAN_ACCEL_XYZ,
				  SENSOR_ATTR_SAMPLING_FREQUENCY, &odr_attr);
	if (ret != 0) {
		LOG_WRN("Cannot set accelerometer sampling frequency: %d", ret);
	}

	ret = sensor_attr_set(dev, SENSOR_CHAN_GYRO_XYZ,
			      SENSOR_ATTR_SAMPLING_FREQUENCY, &odr_attr);
	if (ret != 0) {
		LOG_WRN("Cannot set gyroscope sampling frequency: %d", ret);
	}

	return 0;
}

static void init_erm_motor(void)
{
	LOG_INF("Initializing DRV2605L ERM motor driver");

	drv_write(0x01, 0x00);
	k_msleep(10);

	drv_write(0x1A, 0x36);
	k_msleep(10);

	drv_write(0x03, 0x01);
	k_msleep(10);

	drv_write(0x01, 0x00);
	k_msleep(10);

	LOG_INF("ERM motor ready");
}

static void signal_stats_reset(struct signal_stats *stats)
{
	stats->sum = 0.0f;
	stats->sumsq = 0.0f;
	stats->min = FLT_MAX;
	stats->max = -FLT_MAX;
}

static void window_stats_reset(struct window_stats *stats)
{
	stats->count = 0;
	signal_stats_reset(&stats->gyro_x);
	signal_stats_reset(&stats->gyro_mag);
	signal_stats_reset(&stats->accel_z);
	signal_stats_reset(&stats->acc_motion_mag);
}

static void signal_stats_add(struct signal_stats *stats, float value)
{
	stats->sum += value;
	stats->sumsq += value * value;
	if (value < stats->min) {
		stats->min = value;
	}
	if (value > stats->max) {
		stats->max = value;
	}
}

static void window_stats_add(struct window_stats *stats,
			     float ax, float ay, float az,
			     float gx, float gy, float gz)
{
	float gyro_mag = sqrtf(gx * gx + gy * gy + gz * gz);
	float acc_mag = sqrtf(ax * ax + ay * ay + az * az);
	float acc_motion_mag = fabsf(acc_mag - GRAVITY_MS2);

	stats->count++;
	signal_stats_add(&stats->gyro_x, gx);
	signal_stats_add(&stats->gyro_mag, gyro_mag);
	signal_stats_add(&stats->accel_z, az);
	signal_stats_add(&stats->acc_motion_mag, acc_motion_mag);
}

static float signal_rms(const struct signal_stats *stats, float inv_n)
{
	return sqrtf(stats->sumsq * inv_n);
}

static float signal_std(const struct signal_stats *stats, float inv_n)
{
	float mean = stats->sum * inv_n;
	float variance = stats->sumsq * inv_n - mean * mean;
	return sqrtf((variance > 0.0f) ? variance : 0.0f);
}

static int build_knn_features(const struct window_stats *stats,
			      float features[KNN_FEATURE_COUNT])
{
	if (stats->count < MIN_WINDOW_SAMPLES) {
		return -1;
	}

	float inv_n = 1.0f / (float)stats->count;

	features[0] = signal_rms(&stats->gyro_x, inv_n);
	features[1] = signal_std(&stats->gyro_x, inv_n);
	features[2] = stats->gyro_x.max - stats->gyro_x.min;
	features[3] = signal_std(&stats->gyro_mag, inv_n);
	features[4] = stats->gyro_mag.max;
	features[5] = signal_rms(&stats->gyro_mag, inv_n);
	features[6] = stats->gyro_mag.max - stats->gyro_mag.min;
	features[7] = stats->gyro_mag.sum * inv_n;
	features[8] = stats->accel_z.max;
	features[9] = stats->accel_z.max - stats->accel_z.min;
	features[10] = signal_std(&stats->accel_z, inv_n);
	features[11] = signal_std(&stats->acc_motion_mag, inv_n);

	return 0;
}

static int read_imu_sample(const struct device *imu_dev,
			   float *ax, float *ay, float *az,
			   float *gx, float *gy, float *gz)
{
	struct sensor_value accel[3];
	struct sensor_value gyro[3];

	int ret = sensor_sample_fetch(imu_dev);
	if (ret != 0) {
		return ret;
	}

	ret = sensor_channel_get(imu_dev, SENSOR_CHAN_ACCEL_XYZ, accel);
	if (ret != 0) {
		return ret;
	}

	ret = sensor_channel_get(imu_dev, SENSOR_CHAN_GYRO_XYZ, gyro);
	if (ret != 0) {
		return ret;
	}

	*ax = out_ev(&accel[0]);
	*ay = out_ev(&accel[1]);
	*az = out_ev(&accel[2]);
	*gx = out_ev(&gyro[0]) * GYRO_RAD_TO_DEG;
	*gy = out_ev(&gyro[1]) * GYRO_RAD_TO_DEG;
	*gz = out_ev(&gyro[2]) * GYRO_RAD_TO_DEG;

	return 0;
}

int main(void)
{
	k_msleep(2000);

	if (!device_is_ready(dev_i2c.bus)) {
		LOG_ERR("I2C bus not ready");
		return -1;
	}
	init_erm_motor();

	LOG_INF("Testing haptic alert");
	play_haptic_alert();

	const struct device *const imu_dev = DEVICE_DT_GET(DT_ALIAS(imu0));
	if (!device_is_ready(imu_dev)) {
		LOG_ERR("IMU not ready");
		return -1;
	}

	if (set_sampling_freq(imu_dev) != 0) {
		return -1;
	}

	struct window_stats stats;
	float features[KNN_FEATURE_COUNT];
	window_stats_reset(&stats);

	int64_t window_start_ms = k_uptime_get();
	int64_t last_rotation_ms = window_start_ms;
	int64_t last_haptic_ms = 0;

	LOG_INF("Starting KNN pelvic-rotation detector");

	while (1) {
		float ax;
		float ay;
		float az;
		float gx;
		float gy;
		float gz;

		int ret = read_imu_sample(imu_dev, &ax, &ay, &az, &gx, &gy, &gz);
		if (ret == 0) {
			window_stats_add(&stats, ax, ay, az, gx, gy, gz);
		} else {
			LOG_WRN("IMU sample read failed: %d", ret);
		}

		int64_t now_ms = k_uptime_get();
		if (now_ms - window_start_ms >= WINDOW_DURATION_MS) {
			uint64_t total_start_cycles = k_cycle_get_64();

			if (build_knn_features(&stats, features) == 0) {
				uint64_t knn_start_cycles = k_cycle_get_64();
				uint8_t prediction = knn_predict_pelvic_rotation(features);
				uint64_t knn_elapsed_us =
					k_cyc_to_us_floor64(k_cycle_get_64() - knn_start_cycles);
				uint64_t total_elapsed_us =
					k_cyc_to_us_floor64(k_cycle_get_64() - total_start_cycles);

				if (prediction == KNN_PELVIC_ROTATION) {
					last_rotation_ms = now_ms;
					LOG_INF("KNN: pelvic rotation, samples=%u, infer=%llu us, total=%llu us",
						stats.count,
						(unsigned long long)knn_elapsed_us,
						(unsigned long long)total_elapsed_us);
				} else {
					int64_t inactive_ms = now_ms - last_rotation_ms;
					LOG_INF("KNN: static sitting, inactive=%lld s, samples=%u, infer=%llu us, total=%llu us",
						(long long)(inactive_ms / 1000), stats.count,
						(unsigned long long)knn_elapsed_us,
						(unsigned long long)total_elapsed_us);

					if (inactive_ms >= INACTIVITY_REMINDER_MS &&
					    now_ms - last_haptic_ms >= INACTIVITY_REMINDER_MS) {
						LOG_INF("No pelvic rotation for 10 min -> haptic reminder");
						play_haptic_alert();
						last_haptic_ms = k_uptime_get();
					}
				}
			} else {
				LOG_WRN("Skipping short window, samples=%u", stats.count);
			}

			window_stats_reset(&stats);
			window_start_ms = k_uptime_get();
		}

		k_msleep(POLL_INTERVAL_MS);
	}

	return 0;
}
