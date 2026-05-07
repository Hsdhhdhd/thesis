package com.l1172.bleimuandroid

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothGattDescriptor
import android.bluetooth.BluetoothManager
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.os.Build
import android.os.Handler
import android.os.Looper
import java.util.UUID

data class DiscoveredDevice(
    val name: String,
    val address: String,
    val device: BluetoothDevice,
)

class BleImuManager(
    context: Context,
    private val listener: Listener,
) {
    interface Listener {
        fun onStatus(message: String)
        fun onScanStateChanged(scanning: Boolean)
        fun onDevicesUpdated(devices: List<DiscoveredDevice>)
        fun onConnectionStateChanged(address: String, connected: Boolean, deviceLabel: String?)
        fun onPacketReceived(address: String, packet: ImuPacket)
        fun onError(message: String)
    }

    private val appContext = context.applicationContext
    private val mainHandler = Handler(Looper.getMainLooper())
    private val bluetoothManager =
        appContext.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    private val bluetoothAdapter: BluetoothAdapter? = bluetoothManager.adapter
    private val discoveredDevices = linkedMapOf<String, DiscoveredDevice>()

    // address → gatt
    private val activeGatts = linkedMapOf<String, BluetoothGatt>()
    // address → human-readable label
    private val deviceLabels = linkedMapOf<String, String>()

    private var isScanning = false

    private val scanTimeoutRunnable = Runnable {
        stopScanInternal(notifyComplete = true)
    }

    fun isBluetoothEnabled(): Boolean = bluetoothAdapter?.isEnabled == true

    @SuppressLint("MissingPermission")
    fun startScan() {
        val adapter = bluetoothAdapter
        if (adapter == null) {
            postError("Bluetooth LE is not supported on this phone.")
            return
        }
        if (!adapter.isEnabled) {
            postError("Bluetooth is turned off.")
            return
        }
        val scanner = adapter.bluetoothLeScanner
        if (scanner == null) {
            postError("BLE scanner is unavailable.")
            return
        }

        stopScanInternal(notifyComplete = false)
        discoveredDevices.clear()
        postDevices()

        val settings = ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build()

        scanner.startScan(null, settings, scanCallback)
        isScanning = true
        post { listener.onScanStateChanged(true) }
        postStatus("Scanning for BLE IMU devices...")
        mainHandler.postDelayed(scanTimeoutRunnable, SCAN_WINDOW_MS)
    }

    @SuppressLint("MissingPermission")
    fun connect(address: String, deviceLabel: String? = null) {
        val adapter = bluetoothAdapter
        if (adapter == null) {
            postError("Bluetooth LE is not supported on this phone.")
            return
        }
        if (activeGatts.size >= MAX_CONNECTIONS) {
            postError("Already connected to $MAX_CONNECTIONS devices.")
            return
        }
        if (activeGatts.containsKey(address)) {
            postStatus("Already connected to ${deviceLabels[address] ?: address}.")
            return
        }

        val device = try {
            adapter.getRemoteDevice(address)
        } catch (_: IllegalArgumentException) {
            postError("Invalid Bluetooth address: $address")
            return
        }

        stopScanInternal(notifyComplete = false)
        val label = deviceLabel ?: device.name ?: address
        deviceLabels[address] = label
        postStatus("Connecting to $label...")

        val gatt = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            device.connectGatt(appContext, false, makeGattCallback(address), BluetoothDevice.TRANSPORT_LE)
        } else {
            device.connectGatt(appContext, false, makeGattCallback(address))
        }
        activeGatts[address] = gatt
    }

    @SuppressLint("MissingPermission")
    fun disconnect(address: String) {
        val gatt = activeGatts[address] ?: return
        postStatus("Disconnecting from ${deviceLabels[address] ?: address}...")
        gatt.disconnect()
    }

    fun close() {
        stopScanInternal(notifyComplete = false)
        activeGatts.values.forEach { it.close() }
        activeGatts.clear()
        deviceLabels.clear()
    }

    @SuppressLint("MissingPermission")
    private fun stopScanInternal(notifyComplete: Boolean) {
        if (!isScanning) return
        bluetoothAdapter?.bluetoothLeScanner?.stopScan(scanCallback)
        isScanning = false
        mainHandler.removeCallbacks(scanTimeoutRunnable)
        post {
            listener.onScanStateChanged(false)
            if (notifyComplete) listener.onStatus("Scan complete.")
        }
    }

    private fun postDevices() {
        post { listener.onDevicesUpdated(discoveredDevices.values.toList()) }
    }

    private fun postStatus(message: String) {
        post { listener.onStatus(message) }
    }

    private fun postError(message: String) {
        post { listener.onError(message) }
    }

    private fun post(block: () -> Unit) {
        mainHandler.post(block)
    }

    private val scanCallback = object : ScanCallback() {
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            handleScanResult(result)
        }

        override fun onBatchScanResults(results: MutableList<ScanResult>) {
            results.forEach(::handleScanResult)
        }

        override fun onScanFailed(errorCode: Int) {
            postError("BLE scan failed with error code $errorCode.")
            stopScanInternal(notifyComplete = false)
        }
    }

    @SuppressLint("MissingPermission")
    private fun handleScanResult(result: ScanResult) {
        val scanRecord = result.scanRecord
        val advertisedUuids = scanRecord?.serviceUuids?.map { it.uuid }.orEmpty()
        val device = result.device
        val deviceName = device.name ?: scanRecord?.deviceName ?: "Unknown"

        val looksLikeImuDevice =
            deviceName == DEVICE_NAME || advertisedUuids.contains(IMU_SERVICE_UUID)
        if (!looksLikeImuDevice) return
        if (discoveredDevices.containsKey(device.address)) return

        discoveredDevices[device.address] = DiscoveredDevice(
            name = deviceName,
            address = device.address,
            device = device,
        )
        postDevices()
        postStatus("Found $deviceName (${device.address}).")
    }

    private fun makeGattCallback(address: String) = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (status != BluetoothGatt.GATT_SUCCESS) {
                cleanupGatt(address, gatt)
                postError("GATT error $status for ${deviceLabels[address] ?: address}.")
                post { listener.onConnectionStateChanged(address, false, null) }
                return
            }

            when (newState) {
                BluetoothGatt.STATE_CONNECTED -> {
                    postStatus("Connected to ${deviceLabels[address] ?: address}. Discovering services...")
                    gatt.discoverServices()
                }
                BluetoothGatt.STATE_DISCONNECTED -> {
                    cleanupGatt(address, gatt)
                    postStatus("Disconnected from ${deviceLabels[address] ?: address}.")
                    post { listener.onConnectionStateChanged(address, false, null) }
                }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status != BluetoothGatt.GATT_SUCCESS) {
                cleanupGatt(address, gatt)
                postError("Service discovery failed for ${deviceLabels[address] ?: address}.")
                post { listener.onConnectionStateChanged(address, false, null) }
                return
            }

            val characteristic = gatt
                .getService(IMU_SERVICE_UUID)
                ?.getCharacteristic(IMU_DATA_CHARACTERISTIC_UUID)

            if (characteristic == null) {
                cleanupGatt(address, gatt)
                postError("IMU service not found on ${deviceLabels[address] ?: address}.")
                post { listener.onConnectionStateChanged(address, false, null) }
                return
            }

            enableNotifications(address, gatt, characteristic)
        }

        override fun onDescriptorWrite(
            gatt: BluetoothGatt,
            descriptor: BluetoothGattDescriptor,
            status: Int,
        ) {
            if (descriptor.uuid != CLIENT_CONFIG_DESCRIPTOR_UUID) return

            if (status == BluetoothGatt.GATT_SUCCESS) {
                postStatus("IMU notifications enabled for ${deviceLabels[address] ?: address}.")
                post { listener.onConnectionStateChanged(address, true, deviceLabels[address]) }
            } else {
                cleanupGatt(address, gatt)
                postError("Failed to enable notifications for ${deviceLabels[address] ?: address}.")
                post { listener.onConnectionStateChanged(address, false, null) }
            }
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic,
        ) {
            handleNotification(address, characteristic.value)
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic,
            value: ByteArray,
        ) {
            handleNotification(address, value)
        }
    }

    @SuppressLint("MissingPermission")
    private fun enableNotifications(
        address: String,
        gatt: BluetoothGatt,
        characteristic: BluetoothGattCharacteristic,
    ) {
        if (!gatt.setCharacteristicNotification(characteristic, true)) {
            cleanupGatt(address, gatt)
            postError("Failed to register for notifications.")
            post { listener.onConnectionStateChanged(address, false, null) }
            return
        }

        val descriptor = characteristic.getDescriptor(CLIENT_CONFIG_DESCRIPTOR_UUID)
        if (descriptor == null) {
            cleanupGatt(address, gatt)
            postError("Notification descriptor is missing.")
            post { listener.onConnectionStateChanged(address, false, null) }
            return
        }

        postStatus("Subscribing to IMU notifications for ${deviceLabels[address] ?: address}...")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            gatt.writeDescriptor(descriptor, BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE)
        } else {
            descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
            gatt.writeDescriptor(descriptor)
        }
    }

    private fun handleNotification(address: String, payload: ByteArray?) {
        val packet = payload?.let { ImuPacket.fromPayload(it) } ?: return
        post { listener.onPacketReceived(address, packet) }
    }

    @SuppressLint("MissingPermission")
    private fun cleanupGatt(address: String, gatt: BluetoothGatt) {
        if (activeGatts[address] === gatt) {
            activeGatts.remove(address)
        }
        gatt.close()
    }

    companion object {
        private const val SCAN_WINDOW_MS = 10_000L
        const val MAX_CONNECTIONS = 2
        private const val DEVICE_NAME = "ble-imu-sensor"
        private val IMU_SERVICE_UUID: UUID =
            UUID.fromString("12345678-1234-5678-1234-56789abcdef0")
        private val IMU_DATA_CHARACTERISTIC_UUID: UUID =
            UUID.fromString("12345678-1234-5678-1234-56789abcdef1")
        private val CLIENT_CONFIG_DESCRIPTOR_UUID: UUID =
            UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")
    }
}