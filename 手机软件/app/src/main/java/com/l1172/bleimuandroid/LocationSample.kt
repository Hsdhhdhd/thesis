package com.l1172.bleimuandroid

import android.location.Location
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

data class LocationSample(
    val fixTimestampMillis: Long,
    val fixTimestampText: String,
    val latitude: Double,
    val longitude: Double,
    val accuracyMeters: Float?,
    val altitudeMeters: Double?,
    val speedMetersPerSecond: Float?,
    val bearingDegrees: Float?,
    val provider: String?,
) {
    val summaryText: String
        get() = buildString {
            append("GPS: ")
            append(formatCoordinate(latitude))
            append(", ")
            append(formatCoordinate(longitude))
            accuracyMeters?.let {
                append(" | +/- ")
                append(formatDecimal(it))
                append("m")
            }
            provider?.takeIf { it.isNotBlank() }?.let {
                append(" | ")
                append(it)
            }
        }

    fun toCsvCells(packetTimestampMillis: Long): String {
        val ageMillis = (packetTimestampMillis - fixTimestampMillis).coerceAtLeast(0L)
        return listOf(
            fixTimestampText,
            fixTimestampMillis.toString(),
            formatCoordinate(latitude),
            formatCoordinate(longitude),
            formatDecimal(accuracyMeters),
            formatDecimal(altitudeMeters),
            formatDecimal(speedMetersPerSecond),
            formatDecimal(bearingDegrees),
            provider.orEmpty(),
            ageMillis.toString(),
        ).joinToString(",")
    }

    companion object {
        private val TIMESTAMP_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS", Locale.US)

        fun fromLocation(location: Location): LocationSample {
            val fixMillis = if (location.time > 0L) location.time else System.currentTimeMillis()
            val fixText = TIMESTAMP_FORMATTER.format(
                Instant.ofEpochMilli(fixMillis)
                    .atZone(ZoneId.systemDefault())
                    .toLocalDateTime(),
            )

            return LocationSample(
                fixTimestampMillis = fixMillis,
                fixTimestampText = fixText,
                latitude = location.latitude,
                longitude = location.longitude,
                accuracyMeters = location.accuracy,
                altitudeMeters = location.takeIf { it.hasAltitude() }?.altitude,
                speedMetersPerSecond = location.takeIf { it.hasSpeed() }?.speed,
                bearingDegrees = location.takeIf { it.hasBearing() }?.bearing,
                provider = location.provider?.replace(',', '_'),
            )
        }

        fun csvHeader(): String {
            return listOf(
                "gps_fix_timestamp",
                "gps_fix_epoch_ms",
                "gps_lat",
                "gps_lon",
                "gps_accuracy_m",
                "gps_altitude_m",
                "gps_speed_mps",
                "gps_bearing_deg",
                "gps_provider",
                "gps_age_ms",
            ).joinToString(",")
        }

        fun blankCsvCells(): String = List(10) { "" }.joinToString(",")

        private fun formatCoordinate(value: Double): String =
            String.format(Locale.US, "%.6f", value)

        private fun formatDecimal(value: Float?): String =
            value?.let { String.format(Locale.US, "%.2f", it) }.orEmpty()

        private fun formatDecimal(value: Double?): String =
            value?.let { String.format(Locale.US, "%.2f", it) }.orEmpty()
    }
}
