package com.l1172.bleimuandroid

data class DeviceSummary(
    val name: String,
    val address: String,
) {
    val label: String get() = "$name ($address)"
}

data class DeviceRateStats(
    val instantHz: Float = 0f,
    val averageHz: Float = 0f,
    val packetCount: Int = 0,
)

data class AppState(
    val status: String = "Ready",
    val isScanning: Boolean = false,
    val devices: List<DeviceSummary> = emptyList(),
    val connectedDevices: List<DeviceSummary> = emptyList(),
    val isRecording: Boolean = false,
    val currentRecordingPath: String? = null,
    val lastSavedPath: String? = null,
    val packetCount: Int = 0,
    val lastPackets: Map<String, ImuPacket> = emptyMap(),
    val deviceRates: Map<String, DeviceRateStats> = emptyMap(),
    val lastLocation: LocationSample? = null,
    val locationStatus: String = "GPS: waiting to record",
    val activeAnnotations: Map<String, AnnotationState> = emptyMap(),
    val logLines: List<String> = emptyList(),
) {
    val isConnected: Boolean get() = connectedDevices.isNotEmpty()
    val anyAnnotationActive: Boolean get() = activeAnnotations.isNotEmpty()
}
