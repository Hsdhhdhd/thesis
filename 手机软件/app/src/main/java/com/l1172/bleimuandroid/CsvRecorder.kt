package com.l1172.bleimuandroid

import android.content.Context
import android.os.Environment
import java.io.BufferedWriter
import java.io.File
import java.io.IOException
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class CsvRecorder(private val context: Context) {
    private val writerExecutor: ExecutorService = Executors.newSingleThreadExecutor()

    @Volatile
    private var writer: BufferedWriter? = null

    @Volatile
    private var currentFile: File? = null

    @Synchronized
    @Throws(IOException::class)
    fun start(): File {
        stop()

        val outputDir = File(
            context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS) ?: context.filesDir,
            "BleImu",
        )
        if (!outputDir.exists() && !outputDir.mkdirs()) {
            throw IOException("Unable to create output directory: ${outputDir.absolutePath}")
        }

        val timestamp = LocalDateTime.now().format(
            DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss", Locale.US),
        )
        val file = File(outputDir, "imu_data_$timestamp.csv")
        val bufferedWriter = file.bufferedWriter(Charsets.UTF_8)
        bufferedWriter.write(ImuPacket.csvHeader())
        bufferedWriter.newLine()

        writer = bufferedWriter
        currentFile = file
        return file
    }

    fun append(
        packet: ImuPacket,
        deviceLabel: String,
        locationSample: LocationSample?,
        annotationState: AnnotationState?,
    ) {
        val activeWriter = writer ?: return
        writerExecutor.execute {
            synchronized(this) {
                if (writer !== activeWriter) return@execute
                try {
                    activeWriter.write(packet.toCsvLine(deviceLabel, locationSample, annotationState))
                    activeWriter.newLine()
                } catch (_: IOException) {
                }
            }
        }
    }

    @Synchronized
    fun stop() {
        val activeWriter = writer ?: return
        writer = null
        currentFile = null

        writerExecutor.execute {
            try {
                activeWriter.flush()
                activeWriter.close()
            } catch (_: IOException) {
            }
        }
    }

    fun shutdown() {
        stop()
        writerExecutor.shutdown()
    }

    fun currentFilePath(): String? = currentFile?.absolutePath
}