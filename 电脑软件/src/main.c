#include <zephyr/kernel.h>
#include <limits.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gap.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/dt-bindings/gpio/nordic-nrf-gpio.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>

#define DEVICE_NAME CONFIG_BT_DEVICE_NAME
#define DEVICE_NAME_LEN (sizeof(DEVICE_NAME) - 1)
#define IMU_ODR_HZ 208
#define BLE_NOTIFY_INTERVAL_US 5000

/* Custom Service UUID: 12345678-1234-5678-1234-56789abcdef0 */
#define BT_UUID_IMU_SERVICE_VAL \
    BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x5678, 0x1234, 0x56789abcdef0)

/* IMU Data Characteristic UUID: 12345678-1234-5678-1234-56789abcdef1 */
#define BT_UUID_IMU_DATA_VAL \
    BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x5678, 0x1234, 0x56789abcdef1)

static struct bt_uuid_128 imu_service_uuid = BT_UUID_INIT_128(BT_UUID_IMU_SERVICE_VAL);
static struct bt_uuid_128 imu_data_uuid = BT_UUID_INIT_128(BT_UUID_IMU_DATA_VAL);

/* IMU Data Structure: 6 int16_t values (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z) */
struct imu_data {
    int16_t accel_x;
    int16_t accel_y;
    int16_t accel_z;
    int16_t gyro_x;
    int16_t gyro_y;
    int16_t gyro_z;
} __packed;

static struct imu_data current_imu_data = {
    .accel_x = 0,
    .accel_y = 0,
    .accel_z = 0,
    .gyro_x = 0,
    .gyro_y = 0,
    .gyro_z = 0,
};

static const struct gpio_dt_spec led0 = GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios);
static const struct device *imu_dev = DEVICE_DT_GET(DT_ALIAS(imu0));

static int16_t clamp_i16(int32_t v)
{
    if (v > INT16_MAX) {
        return INT16_MAX;
    }
    if (v < INT16_MIN) {
        return INT16_MIN;
    }
    return (int16_t)v;
}

static int32_t imu_sensor_value_to_milli(const struct sensor_value *val)
{
    /* val1: integer part, val2: fractional in 1e-6 */
    return val->val1 * 1000 + val->val2 / 1000;
}

static int set_sampling_freq(const struct device *dev)
{
    struct sensor_value odr_attr = { .val1 = IMU_ODR_HZ, .val2 = 0 };

    int ret = sensor_attr_set(dev, SENSOR_CHAN_ACCEL_XYZ,
                              SENSOR_ATTR_SAMPLING_FREQUENCY, &odr_attr);
    if (ret) {
        return ret;
    }

    ret = sensor_attr_set(dev, SENSOR_CHAN_GYRO_XYZ,
                          SENSOR_ATTR_SAMPLING_FREQUENCY, &odr_attr);
    if (ret) {
        return ret;
    }

    return 0;
}

static int fetch_and_update_imu(void)
{
    struct sensor_value ax, ay, az, gx, gy, gz;

    int ret = sensor_sample_fetch(imu_dev);
    if (ret) {
        return ret;
    }

    ret = sensor_channel_get(imu_dev, SENSOR_CHAN_ACCEL_X, &ax);
    ret |= sensor_channel_get(imu_dev, SENSOR_CHAN_ACCEL_Y, &ay);
    ret |= sensor_channel_get(imu_dev, SENSOR_CHAN_ACCEL_Z, &az);
    ret |= sensor_channel_get(imu_dev, SENSOR_CHAN_GYRO_X, &gx);
    ret |= sensor_channel_get(imu_dev, SENSOR_CHAN_GYRO_Y, &gy);
    ret |= sensor_channel_get(imu_dev, SENSOR_CHAN_GYRO_Z, &gz);
    if (ret) {
        return ret;
    }

    /* Convert to milli-units and clamp to int16 */
    current_imu_data.accel_x = clamp_i16(imu_sensor_value_to_milli(&ax));
    current_imu_data.accel_y = clamp_i16(imu_sensor_value_to_milli(&ay));
    current_imu_data.accel_z = clamp_i16(imu_sensor_value_to_milli(&az));
    current_imu_data.gyro_x  = clamp_i16(imu_sensor_value_to_milli(&gx));
    current_imu_data.gyro_y  = clamp_i16(imu_sensor_value_to_milli(&gy));
    current_imu_data.gyro_z  = clamp_i16(imu_sensor_value_to_milli(&gz));

    return 0;
}

static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR),
    BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),
};

static const struct bt_data sd[] = {
    BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_IMU_SERVICE_VAL),
};

/* GATT Read Callback for IMU Data */
static ssize_t read_imu_data(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                              void *buf, uint16_t len, uint16_t offset)
{
    return bt_gatt_attr_read(conn, attr, buf, len, offset, 
                             &current_imu_data, sizeof(struct imu_data));
}

/* GATT CCC (Client Characteristic Configuration) Changed Callback */
/* GATT CCC (Client Characteristic Configuration) Changed Callback */
static void imu_ccc_cfg_changed(const struct bt_gatt_attr *attr, uint16_t value);

/* Define GATT Service */
BT_GATT_SERVICE_DEFINE(imu_service,
    BT_GATT_PRIMARY_SERVICE(&imu_service_uuid),
    
    BT_GATT_CHARACTERISTIC(&imu_data_uuid.uuid,
                          BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY,
                          BT_GATT_PERM_READ,
                          read_imu_data, NULL, NULL),
    
    BT_GATT_CCC(imu_ccc_cfg_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
);

static bool device_connected = false;

static void connected(struct bt_conn *conn, uint8_t err)
{
    if (err) {
        /* Connection failed */
    } else {
        device_connected = true;
        gpio_pin_set_dt(&led0, 1);  /* LED ON when connected */
    }
}

static void disconnected(struct bt_conn *conn, uint8_t reason)
{
    device_connected = false;
    gpio_pin_set_dt(&led0, 0);  /* LED OFF when disconnected */

    int err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
    (void)err; /* Suppress unused variable warning */
}

static void imu_ccc_cfg_changed(const struct bt_gatt_attr *attr, uint16_t value)
{
    /* Notification state changed */
    (void)attr;
    (void)value;
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
    .connected = connected,
    .disconnected = disconnected,
};

int main(void)
{
    int err;

    /* 添加启动延迟，确保外设稳定 */
    k_sleep(K_MSEC(100));

    if (!device_is_ready(imu_dev)) {
        return -1;
    }

    err = set_sampling_freq(imu_dev);
    if (err) {
        return -1;
    }

    if (!gpio_is_ready_dt(&led0)) {
        return -1;
    }

    err = gpio_pin_configure_dt(&led0, GPIO_OUTPUT_INACTIVE);
    if (err) {
        return -1;
    }

    err = bt_enable(NULL);
    if (err) {
        return -1;
    }

    err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
    if (err) {
        return -1;
    }

    while (1) {
        if (device_connected) {
            /* Poll IMU once per loop before sending */
            fetch_and_update_imu();

            /* 构建 IMU 数据包 (12 字节) */
            uint8_t data[12];
            int16_t values[] = {
                current_imu_data.accel_x,
                current_imu_data.accel_y,
                current_imu_data.accel_z,
                current_imu_data.gyro_x,
                current_imu_data.gyro_y,
                current_imu_data.gyro_z
            };
            
            /* 转换为小端字节序 */
            for (int i = 0; i < 6; i++) {
                data[i*2] = values[i] & 0xFF;
                data[i*2+1] = (values[i] >> 8) & 0xFF;
            }

            /* 发送 Notify */
            const struct bt_gatt_attr *attr = &imu_service.attrs[2]; /* IMU 特征属性 */
            bt_gatt_notify(NULL, attr, data, sizeof(data));
            
            k_sleep(K_USEC(BLE_NOTIFY_INTERVAL_US));
        } else {
            k_sleep(K_MSEC(500));
        }
    }

    return 0;
}
