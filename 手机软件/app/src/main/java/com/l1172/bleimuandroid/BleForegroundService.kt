package com.l1172.bleimuandroid

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.os.Binder
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import java.util.ArrayDeque
import java.util.Locale

class BleForegroundService : Service(), BleImuManager.Listener, LocationTracker.Listener {
    interface UiListener {
        fun onStateChanged(state: AppState)
    }

    inner class LocalBinder : Binder() {
        fun getService(): BleForegroundService = this@BleForegroundService
    }

    private val binder = LocalBinder()
    private val logLines = ArrayDeque<String>()
    private val timeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss", Locale.US)
    private val reconnectHandler = Handler(Looper.getMainLooper())

    private lateinit var bleImuManager: BleImuManager
    private lateinit var csvRecorder: CsvRecorder
    private lateinit var locationTracker: LocationTracker

    private var uiListener: UiListener? = null
    private var isBoundToUi = false

    private val connectedDevices = linkedMapOf<String, String>()
    private val desiredDevices = linkedMapOf<String, String>()
    private val reconnectRunnables = linkedMapOf<String, Runnable>()
    private val manualDisconnects = mutableSetOf<String>()
    private val activeAnnotations = linkedMapOf<String, AnnotationState>()
    private var nextAnnotationSegmentId = 1L

    private var currentStatus = "Ready"
    private var isScanning = false
    private var discoveredDevices: List<DiscoveredDevice> = emptyList()
    private var isRecording = false
    private var currentRecordingPath: String? = null
    private var lastSavedPath: String? = null
    private var packetCount = 0
    private val deviceRateMeters = linkedMapOf<String, DeviceRateMeter>()
    private val lastPackets = linkedMapOf<String, ImuPacket>()  // address → last packet
    private var lastLocation: LocationSample? = null
    private var locationStatus = "GPS: waiting to record"
    private var hasLoggedLocationFix = false
    private var currentForegroundServiceType = ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE
    private var isForegroundStarted = false

    override fun onCreate() {
        super.onCreate()
        bleImuManager = BleImuManager(this, this)
        csvRecorder = CsvRecorder(this)
        locationTracker = LocationTracker(this, this)
        createNotificationChannel()
        appendLog("Service created.")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        promoteToForegroundIfNeeded()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder {
        isBoundToUi = true
        return binder
    }

    override fun onUnbind(intent: Intent?): Boolean {
        isBoundToUi = false
        uiListener = null
        maybeStopIfIdle()
        return true
    }

    override fun onDestroy() {
        reconnectRunnables.values.forEach { reconnectHandler.removeCallbacks(it) }
        reconnectRunnables.clear()
        if (isRecording) stopRecordingInternal("Recording stopped because the service was destroyed.")
        locationTracker.stop()
        bleImuManager.close()
        csvRecorder.shutdown()
        super.onDestroy()
    }

    fun setUiListener(listener: UiListener?) {
        uiListener = listener
        notifyUi()
    }

    fun snapshotState(): AppState = AppState(
        status = currentStatus,
        isScanning = isScanning,
        devices = discoveredDevices.map { DeviceSummary(it.name, it.address) },
        connectedDevices = connectedDevices.map { (addr, label) -> DeviceSummary(label, addr) },
        isRecording = isRecording,
        currentRecordingPath = currentRecordingPath,
        lastSavedPath = lastSavedPath,
        packetCount = packetCount,
        lastPackets = lastPackets.toMap(),
        deviceRates = deviceRateMeters.mapValues { (_, meter) -> meter.snapshot() },
        lastLocation = lastLocation,
        locationStatus = locationStatus,
        activeAnnotations = activeAnnotations.toMap(),
        logLines = logLines.toList(),
    )

    fun isBluetoothEnabled(): Boolean = bleImuManager.isBluetoothEnabled()

    fun startScan() {
        promoteToForegroundIfNeeded()
        bleImuManager.startScan()
    }

    fun connect(address: String) {
        promoteToForegroundIfNeeded()
        val label = discoveredDevices.firstOrNull { it.address == address }?.name ?: address
        desiredDevices[address] = label
        manualDisconnects.remove(address)
        cancelReconnect(address)
        bleImuManager.connect(address, label)
    }

    fun disconnect(address: String) {
        manualDisconnects.add(address)
        desiredDevices.remove(address)
        cancelReconnect(address)
        bleImuManager.disconnect(address)
    }

    fun startRecording() {
        if (connectedDevices.isEmpty()) { onError("Connect to the IMU before recording."); return }
        if (!hasLocationPermission()) { onError("Location permission is required before recording GPS data."); return }
        if (isRecording) return
        try {
            promoteToForegroundIfNeeded()
            val file = csvRecorder.start()
            isRecording = true
            currentRecordingPath = file.absolutePath
            lastSavedPath = file.absolutePath
            currentStatus = "Recording IMU + GPS data"
            lastLocation = null
            locationStatus = "GPS: acquiring fix..."
            hasLoggedLocationFix = false
            activeAnnotations.clear()
            nextAnnotationSegmentId = 1L
            locationTracker.start()
            refreshForegroundServiceType()
            appendLog("Recording started: ${file.absolutePath}")
            refreshNotification()
            notifyUi()
        } catch (error: Exception) {
            onError("Recording start failed: ${error.message}")
        }
    }

    fun stopRecording() = stopRecordingInternal("Recording stopped.")

    fun startAnnotation(address: String, rawLabel: String) {
        if (!isRecording) { onError("Start recording before starting an annotation."); return }
        if (activeAnnotations.containsKey(address)) {
            onError("Stop the current annotation for ${connectedDevices[address] ?: address} first.")
            return
        }
        val label = normalizeAnnotationLabel(rawLabel)
        if (label.isBlank()) { onError("Enter a label name before starting an annotation."); return }
        val annotation = AnnotationState.start(label, nextAnnotationSegmentId)
        nextAnnotationSegmentId += 1
        activeAnnotations[address] = annotation
        appendLog("Annotation [${connectedDevices[address] ?: address}] started: $label (#${annotation.segmentId})")
        refreshNotification()
        notifyUi()
    }

    fun stopAnnotation(address: String) {
        val annotation = activeAnnotations.remove(address) ?: return
        appendLog("Annotation [${connectedDevices[address] ?: address}] ended: ${annotation.label} (#${annotation.segmentId})")
        refreshNotification()
        notifyUi()
    }

    override fun onStatus(message: String) {
        currentStatus = message
        appendLog(message)
        refreshNotification()
        notifyUi()
    }

    override fun onScanStateChanged(scanning: Boolean) {
        isScanning = scanning
        refreshNotification()
        notifyUi()
        maybeStopIfIdle()
    }

    override fun onDevicesUpdated(devices: List<DiscoveredDevice>) {
        discoveredDevices = devices
        notifyUi()
    }

    override fun onConnectionStateChanged(address: String, connected: Boolean, deviceLabel: String?) {
        if (connected) {
            connectedDevices[address] = deviceLabel ?: address
            cancelReconnect(address)
            manualDisconnects.remove(address)
            currentStatus = buildConnectedStatus()
            appendLog("Connected to ${deviceLabel ?: address}.")
        } else {
            val label = connectedDevices.remove(address) ?: desiredDevices[address] ?: address
            activeAnnotations.remove(address)
            lastPackets.remove(address)
            deviceRateMeters.remove(address)
            when {
                address in manualDisconnects -> {
                    manualDisconnects.remove(address)
                    appendLog("Disconnected from $label.")
                    if (connectedDevices.isEmpty() && reconnectRunnables.isEmpty() && isRecording) {
                        stopRecordingInternal("Recording stopped: all devices disconnected.")
                    }
                    currentStatus = if (connectedDevices.isNotEmpty()) buildConnectedStatus() else "Disconnected"
                }
                desiredDevices.containsKey(address) -> {
                    scheduleReconnect(address)
                    refreshNotification()
                    notifyUi()
                    maybeStopIfIdle()
                    return
                }
                else -> {
                    appendLog("Disconnected from $label.")
                    if (connectedDevices.isEmpty() && isRecording) {
                        stopRecordingInternal("Recording stopped: connection closed.")
                    }
                    currentStatus = if (connectedDevices.isNotEmpty()) buildConnectedStatus() else "Disconnected"
                }
            }
        }
        refreshNotification()
        notifyUi()
        maybeStopIfIdle()
    }

    override fun onPacketReceived(address: String, packet: ImuPacket) {
        packetCount += 1
        lastPackets[address] = packet
        deviceRateMeters.getOrPut(address) { DeviceRateMeter() }.record(packet.timestampMillis)
        if (isRecording) {
            csvRecorder.append(packet, address, lastLocation, activeAnnotations[address])
        }
        if (packetCount % 5 == 0) {
            if (packetCount % 100 == 0) refreshNotification()
            notifyUi()
        }
    }

    override fun onError(message: String) {
        currentStatus = message
        appendLog("Error: $message")
        refreshNotification()
        notifyUi()
    }

    override fun onLocationUpdated(sample: LocationSample) {
        lastLocation = sample
        locationStatus = sample.summaryText
        if (isRecording && !hasLoggedLocationFix) {
            appendLog("GPS fix acquired.")
            hasLoggedLocationFix = true
        }
        notifyUi()
    }

    override fun onLocationStatus(message: String) {
        if (locationStatus == message) return
        locationStatus = message
        appendLog(message)
        notifyUi()
    }

    override fun onLocationUnavailable(message: String) {
        lastLocation = null
        if (locationStatus == message) return
        locationStatus = message
        appendLog(message)
        notifyUi()
    }

    private fun stopRecordingInternal(logMessage: String) {
        if (!isRecording) return
        activeAnnotations.clear()
        csvRecorder.stop()
        locationTracker.stop()
        isRecording = false
        currentRecordingPath = null
        locationStatus = lastLocation?.summaryText ?: "GPS: waiting to record"
        currentStatus = if (connectedDevices.isNotEmpty()) buildConnectedStatus() else "Ready"
        appendLog(logMessage)
        refreshForegroundServiceType()
        refreshNotification()
        notifyUi()
        maybeStopIfIdle()
    }

    private fun notifyUi() = uiListener?.onStateChanged(snapshotState())

    private fun appendLog(message: String) {
        val timestamp = LocalTime.now().format(timeFormatter)
        logLines.addLast("[$timestamp] $message")
        while (logLines.size > MAX_LOG_LINES) logLines.removeFirst()
    }

    private fun scheduleReconnect(address: String) {
        val label = desiredDevices[address] ?: address
        cancelReconnect(address)
        val runnable = Runnable {
            reconnectRunnables.remove(address)
            if (desiredDevices.containsKey(address)) {
                currentStatus = "Reconnecting to $label..."
                appendLog(currentStatus)
                refreshNotification()
                notifyUi()
                bleImuManager.connect(address, label)
            }
        }
        reconnectRunnables[address] = runnable
        reconnectHandler.postDelayed(runnable, RECONNECT_DELAY_MS)
        currentStatus = if (connectedDevices.isNotEmpty()) {
            "${buildConnectedStatus()} | Retrying $label in ${RECONNECT_DELAY_MS / 1000}s..."
        } else {
            "Disconnected from $label. Retrying in ${RECONNECT_DELAY_MS / 1000}s..."
        }
        appendLog("Connection lost to $label. Auto reconnect scheduled.")
        promoteToForegroundIfNeeded()
    }

    private fun cancelReconnect(address: String) {
        reconnectRunnables.remove(address)?.let { reconnectHandler.removeCallbacks(it) }
    }

    private fun buildConnectedStatus(): String =
        "Connected to ${connectedDevices.values.joinToString(" + ")}"

    private fun maybeStopIfIdle() {
        if (isBoundToUi || connectedDevices.isNotEmpty() || isRecording || isScanning || reconnectRunnables.isNotEmpty()) return
        stopForegroundCompat()
        stopSelf()
    }

    private fun refreshNotification() {
        if (!isForegroundStarted) return
        getSystemService(NotificationManager::class.java).notify(NOTIFICATION_ID, buildNotification())
    }

    private fun refreshForegroundServiceType() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) return
        val newType = ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE or
            if (isRecording && hasLocationPermission()) ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION else 0
        if (newType == currentForegroundServiceType) return
        currentForegroundServiceType = newType
        if (isForegroundStarted) startForegroundCompat(buildNotification())
    }

    private fun buildNotification(): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val title = when {
            isRecording -> "imu receiver recording"
            connectedDevices.isNotEmpty() -> "imu receiver connected"
            isScanning -> "imu receiver scanning"
            else -> "imu receiver ready"
        }
        val text = when {
            isRecording -> buildString {
                append(connectedDevices.values.joinToString(" + "))
                append(" | packets: $packetCount | ")
                append(locationStatus.removePrefix("GPS: "))
                if (activeAnnotations.isNotEmpty()) {
                    append(" | labels: ")
                    append(activeAnnotations.values.joinToString(", ") { it.label })
                }
            }
            connectedDevices.isNotEmpty() -> "${connectedDevices.values.joinToString(" + ")} | packets: $packetCount"
            isScanning -> "Searching for ble-imu-sensor"
            else -> currentStatus
        }
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title).setContentText(text)
            .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
            .setContentIntent(pendingIntent)
            .setOngoing(true).setOnlyAlertOnce(true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(CHANNEL_ID, "imu receiver", NotificationManager.IMPORTANCE_LOW).apply {
            description = "Keeps IMU and GPS collection running while the app is in the background."
        }
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    private fun startForegroundCompat(notification: Notification) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIFICATION_ID, notification, currentForegroundServiceType)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
        isForegroundStarted = true
    }

    private fun stopForegroundCompat() {
        if (!isForegroundStarted) return
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) stopForeground(STOP_FOREGROUND_REMOVE)
        else @Suppress("DEPRECATION") stopForeground(true)
        isForegroundStarted = false
    }

    private fun promoteToForegroundIfNeeded() {
        if (isForegroundStarted) { refreshNotification(); return }
        startForegroundCompat(buildNotification())
    }

    private fun hasLocationPermission() =
        ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED

    private fun normalizeAnnotationLabel(rawLabel: String) =
        rawLabel.replace(',', ' ').replace('\n', ' ').replace('\r', ' ').trim().replace(Regex("\\s+"), " ")

    private class DeviceRateMeter {
        private val recentPacketTimes = ArrayDeque<Long>()
        private var firstPacketMillis: Long? = null
        private var lastPacketMillis: Long? = null
        private var packetCount: Int = 0

        fun record(timestampMillis: Long) {
            if (firstPacketMillis == null) firstPacketMillis = timestampMillis
            lastPacketMillis = timestampMillis
            packetCount += 1
            recentPacketTimes.addLast(timestampMillis)

            val cutoff = timestampMillis - RATE_WINDOW_MS
            while (recentPacketTimes.size > 1 && recentPacketTimes.first < cutoff) {
                recentPacketTimes.removeFirst()
            }
        }

        fun snapshot(): DeviceRateStats {
            val instantHz = calculateHz(
                count = recentPacketTimes.size,
                firstMillis = recentPacketTimes.firstOrNull(),
                lastMillis = recentPacketTimes.lastOrNull(),
            )
            val averageHz = calculateHz(
                count = packetCount,
                firstMillis = firstPacketMillis,
                lastMillis = lastPacketMillis,
            )
            return DeviceRateStats(
                instantHz = instantHz,
                averageHz = averageHz,
                packetCount = packetCount,
            )
        }

        private fun calculateHz(count: Int, firstMillis: Long?, lastMillis: Long?): Float {
            if (count < 2 || firstMillis == null || lastMillis == null || lastMillis <= firstMillis) {
                return 0f
            }
            return ((count - 1) * 1000f) / (lastMillis - firstMillis)
        }

        companion object {
            private const val RATE_WINDOW_MS = 1000L
        }
    }

    companion object {
        private const val CHANNEL_ID = "ble_imu_receiver_channel"
        private const val NOTIFICATION_ID = 1001
        private const val MAX_LOG_LINES = 30
        private const val RECONNECT_DELAY_MS = 3000L
    }
}
