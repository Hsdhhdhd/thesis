package com.l1172.bleimuandroid

import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

data class ImuPacket(
    val timestampMillis: Long,
    val timestampText: String,
    val accelX: Float,
    val accelY: Float,
    val accelZ: Float,
    val gyroX: Float,
    val gyroY: Float,
    val gyroZ: Float,
) {
    fun toCsvLine(deviceLabel: String, locationSample: LocationSample?, annotationState: AnnotationState?): String {
        return listOf(
            deviceLabel,
            timestampText,
            timestampMillis.toString(),
            format(accelX),
            format(accelY),
            format(accelZ),
            format(gyroX),
            format(gyroY),
            format(gyroZ),
            locationSample?.toCsvCells(timestampMillis) ?: LocationSample.blankCsvCells(),
            annotationState?.toCsvCells() ?: AnnotationState.blankCsvCells(),
        ).joinToString(",")
    }

    companion object {
        private const val GYRO_MILLI_RAD_TO_DEG_PER_SEC = 0.0572957795f
        private val TIMESTAMP_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS", Locale.US)

        fun fromPayload(payload: ByteArray, receivedAtMillis: Long = System.currentTimeMillis()): ImuPacket? {
            if (payload.size < 12) return null

            val buffer = ByteBuffer.wrap(payload).order(ByteOrder.LITTLE_ENDIAN)
            val accelXRaw = buffer.short.toInt()
            val accelYRaw = buffer.short.toInt()
            val accelZRaw = buffer.short.toInt()
            val gyroXRaw = buffer.short.toInt()
            val gyroYRaw = buffer.short.toInt()
            val gyroZRaw = buffer.short.toInt()

            val timestampText = TIMESTAMP_FORMATTER.format(
                Instant.ofEpochMilli(receivedAtMillis)
                    .atZone(ZoneId.systemDefault())
                    .toLocalDateTime(),
            )

            return ImuPacket(
                timestampMillis = receivedAtMillis,
                timestampText = timestampText,
                accelX = accelXRaw / 1000f,
                accelY = accelYRaw / 1000f,
                accelZ = accelZRaw / 1000f,
                gyroX = gyroXRaw * GYRO_MILLI_RAD_TO_DEG_PER_SEC,
                gyroY = gyroYRaw * GYRO_MILLI_RAD_TO_DEG_PER_SEC,
                gyroZ = gyroZRaw * GYRO_MILLI_RAD_TO_DEG_PER_SEC,
            )
        }

        fun csvHeader(): String {
            return listOf(
                "device_label",
                "timestamp",
                "epoch_ms",
                "accel_x",
                "accel_y",
                "accel_z",
                "gyro_x",
                "gyro_y",
                "gyro_z",
                LocationSample.csvHeader(),
                AnnotationState.csvHeader(),
            ).joinToString(",")
        }

        private fun format(value: Float): String = String.format(Locale.US, "%.5f", value)
    }
}