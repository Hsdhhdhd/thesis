package com.l1172.bleimuandroid

import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

data class AnnotationState(
    val label: String,
    val segmentId: Long,
    val startedAtMillis: Long,
    val startedAtText: String,
) {
    fun toCsvCells(): String {
        return listOf(
            csvCell(label),
            segmentId.toString(),
            startedAtText,
            startedAtMillis.toString(),
        ).joinToString(",")
    }

    companion object {
        private val TIMESTAMP_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS", Locale.US)

        fun start(label: String, segmentId: Long, startedAtMillis: Long = System.currentTimeMillis()): AnnotationState {
            val startedAtText = TIMESTAMP_FORMATTER.format(
                Instant.ofEpochMilli(startedAtMillis)
                    .atZone(ZoneId.systemDefault())
                    .toLocalDateTime(),
            )
            return AnnotationState(
                label = label,
                segmentId = segmentId,
                startedAtMillis = startedAtMillis,
                startedAtText = startedAtText,
            )
        }

        fun csvHeader(): String {
            return listOf(
                "annotation_label",
                "annotation_segment_id",
                "annotation_started_timestamp",
                "annotation_started_epoch_ms",
            ).joinToString(",")
        }

        fun blankCsvCells(): String = List(4) { "" }.joinToString(",")

        private fun csvCell(value: String): String {
            if (value.none { it == ',' || it == '"' || it == '\n' || it == '\r' }) {
                return value
            }

            return "\"" + value.replace("\"", "\"\"") + "\""
        }
    }
}
