package com.l1172.bleimuandroid

import android.Manifest
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.content.res.ColorStateList
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.Bundle
import android.os.IBinder
import android.text.InputType
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.ArrayAdapter
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.ColorRes
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import com.google.android.material.chip.Chip
import com.google.android.material.chip.ChipGroup
import com.l1172.bleimuandroid.databinding.ActivityMainBinding
import java.io.File
import java.util.Locale

class MainActivity : AppCompatActivity(), BleForegroundService.UiListener {
    private lateinit var binding: ActivityMainBinding
    private lateinit var deviceAdapter: ArrayAdapter<String>

    private var bleService: BleForegroundService? = null
    private var isBound = false
    private var currentState = AppState()

    private var lastRenderedConnectedDevices: List<DeviceSummary> = emptyList()
    private var lastRenderedAnnotations: Map<String, AnnotationState> = emptyMap()
    private var lastRenderedIsRecording: Boolean = false
    private var lastRenderedTelemetryDevices: Set<String> = emptySet()
    private var lastSpinnerItems: List<String> = emptyList()

    private var pendingAction = PendingAction.NONE

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { result ->
            val granted = result.values.all { it }
            if (!granted) {
                showToast("Bluetooth, location, and notification permissions are required.")
                pendingAction = PendingAction.NONE
                return@registerForActivityResult
            }
            when (pendingAction) {
                PendingAction.SCAN -> startScan()
                PendingAction.CONNECT -> connectSelectedDevice()
                PendingAction.RECORD -> startRecording()
                PendingAction.NONE -> Unit
            }
            pendingAction = PendingAction.NONE
        }

    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            val binder = service as? BleForegroundService.LocalBinder ?: return
            bleService = binder.getService()
            bleService?.setUiListener(this@MainActivity)
            currentState = bleService?.snapshotState() ?: AppState()
            forceRenderAll(currentState)
            refreshButtons()
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            bleService = null
            isBound = false
            refreshButtons()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        deviceAdapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_item,
            mutableListOf("No devices yet"),
        ).apply {
            setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        }
        binding.deviceSpinner.adapter = deviceAdapter

        binding.scanButton.setOnClickListener {
            if (ensureRuntimePermissions(PendingAction.SCAN)) startScan()
        }
        binding.connectButton.setOnClickListener {
            if (ensureRuntimePermissions(PendingAction.CONNECT)) connectSelectedDevice()
        }
        binding.startRecordingButton.setOnClickListener {
            if (ensureRuntimePermissions(PendingAction.RECORD)) startRecording()
        }
        binding.stopRecordingButton.setOnClickListener { bleService?.stopRecording() }
        binding.shareButton.setOnClickListener { shareLastFile() }
        binding.editLabelsButton.setOnClickListener { showEditLabelsDialog() }

        if (!packageManager.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH_LE)) {
            binding.statusText.text = "This phone does not support Bluetooth LE."
        }
        refreshButtons()
    }

    override fun onStart() {
        super.onStart()
        val serviceIntent = Intent(this, BleForegroundService::class.java)
        isBound = bindService(serviceIntent, serviceConnection, Context.BIND_AUTO_CREATE)
        refreshButtons()
    }

    override fun onStop() {
        if (isBound) {
            bleService?.setUiListener(null)
            unbindService(serviceConnection)
            isBound = false
        }
        bleService = null
        super.onStop()
    }

    override fun onStateChanged(state: AppState) {
        currentState = state
        renderState(state)
        refreshButtons()
    }

    private fun forceRenderAll(state: AppState) {
        lastRenderedConnectedDevices = emptyList()
        lastRenderedAnnotations = emptyMap()
        lastRenderedIsRecording = !state.isRecording
        lastRenderedTelemetryDevices = emptySet()
        lastSpinnerItems = emptyList()
        renderState(state)
    }

    private fun renderState(state: AppState) {
        binding.statusText.text = state.status
        binding.scanButton.text = if (state.isScanning) "Scanning..." else getString(R.string.scan_devices)
        binding.recordingPathText.text = when {
            state.isRecording && state.currentRecordingPath != null -> "Recording to\n${state.currentRecordingPath}"
            state.lastSavedPath != null -> "Last file\n${state.lastSavedPath}"
            else -> getString(R.string.recording_not_started)
        }

        val newDeviceLabels = if (state.devices.isEmpty()) {
            listOf("No IMU devices found")
        } else {
            state.devices.map(DeviceSummary::label)
        }
        if (newDeviceLabels != lastSpinnerItems) {
            lastSpinnerItems = newDeviceLabels
            deviceAdapter.clear()
            deviceAdapter.addAll(newDeviceLabels)
            deviceAdapter.notifyDataSetChanged()
        }

        binding.packetCountText.text = String.format(Locale.US, "%,d", state.packetCount)
        binding.gpsText.text = state.lastLocation?.summaryText ?: state.locationStatus
        binding.logText.text = if (state.logLines.isEmpty()) {
            getString(R.string.log_placeholder)
        } else {
            state.logLines.joinToString("\n")
        }

        val telemetryDevices = state.connectedDevices.map(DeviceSummary::address).toSet()
        if (telemetryDevices != lastRenderedTelemetryDevices) {
            renderLiveDataRows(state)
            lastRenderedTelemetryDevices = telemetryDevices
        } else {
            updateLiveDataRows(state)
        }

        val devicesChanged = state.connectedDevices != lastRenderedConnectedDevices
        val annotationsChanged = state.activeAnnotations != lastRenderedAnnotations
        val recordingChanged = state.isRecording != lastRenderedIsRecording
        if (devicesChanged || annotationsChanged || recordingChanged) {
            renderConnectedDevices(state)
            lastRenderedConnectedDevices = state.connectedDevices
            lastRenderedAnnotations = state.activeAnnotations.toMap()
            lastRenderedIsRecording = state.isRecording
        }
    }

    private fun liveRowTag(address: String) = "live_$address"

    private fun renderLiveDataRows(state: AppState) {
        binding.liveDataContainer.removeAllViews()
        if (state.connectedDevices.isEmpty()) {
            binding.liveDataContainer.addView(
                buildEmptyPanel(
                    title = "Waiting for a live sensor feed",
                    subtitle = "Connect a BLE IMU device to see fresh rate and motion values here.",
                ),
            )
            return
        }

        state.connectedDevices.forEachIndexed { index, device ->
            val packet = state.lastPackets[device.address]
            val rateStats = state.deviceRates[device.address]
            val card = buildDashboardCard().apply {
                tag = liveRowTag(device.address)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                ).also { params ->
                    if (index > 0) params.topMargin = dp(12)
                }
            }

            val content = buildCardColumn()
            val headerRow = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
            }
            val titleColumn = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            }
            titleColumn.addView(
                TextView(this).apply {
                    tag = "device_name"
                    text = device.name
                    setTextColor(color(R.color.dashboard_text_primary))
                    setTypeface(null, Typeface.BOLD)
                    setTextSize(TypedValue.COMPLEX_UNIT_SP, 17f)
                },
            )
            titleColumn.addView(
                TextView(this).apply {
                    tag = "device_address"
                    text = device.address
                    setTextColor(color(R.color.dashboard_text_secondary))
                    setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
                },
            )
            headerRow.addView(titleColumn)
            headerRow.addView(
                buildInfoPill(
                    text = rateText(rateStats),
                    backgroundColor = color(R.color.dashboard_accent_soft),
                    textColor = color(R.color.dashboard_accent),
                    tag = "rate",
                ),
            )
            content.addView(headerRow)
            content.addView(
                buildMetricPanel(
                    title = "Acceleration",
                    value = accelText(packet),
                    valueTag = "accel",
                ).apply {
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    ).also { params -> params.topMargin = dp(14) }
                },
            )
            content.addView(
                buildMetricPanel(
                    title = "Gyroscope",
                    value = gyroText(packet),
                    valueTag = "gyro",
                ).apply {
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    ).also { params -> params.topMargin = dp(10) }
                },
            )

            card.addView(content)
            binding.liveDataContainer.addView(card)
        }
    }

    private fun updateLiveDataRows(state: AppState) {
        for (i in 0 until binding.liveDataContainer.childCount) {
            val row = binding.liveDataContainer.getChildAt(i)
            val address = (row.tag as? String)?.removePrefix("live_") ?: continue
            val device = state.connectedDevices.firstOrNull { it.address == address } ?: continue
            val packet = state.lastPackets[address]
            row.findViewWithTag<TextView>("device_name")?.text = device.name
            row.findViewWithTag<TextView>("device_address")?.text = address
            row.findViewWithTag<TextView>("rate")?.text = rateText(state.deviceRates[address])
            row.findViewWithTag<TextView>("accel")?.text = accelText(packet)
            row.findViewWithTag<TextView>("gyro")?.text = gyroText(packet)
        }
    }

    private fun accelText(packet: ImuPacket?): String = if (packet == null) {
        "Waiting for packets"
    } else {
        "X ${format(packet.accelX)}   Y ${format(packet.accelY)}   Z ${format(packet.accelZ)} m/s^2"
    }

    private fun gyroText(packet: ImuPacket?): String = if (packet == null) {
        "Waiting for packets"
    } else {
        "X ${format(packet.gyroX)}   Y ${format(packet.gyroY)}   Z ${format(packet.gyroZ)} deg/s"
    }

    private fun rateText(stats: DeviceRateStats?): String = if (stats == null || stats.packetCount == 0) {
        "Awaiting data"
    } else {
        "${format(stats.instantHz)} Hz"
    }

    private fun renderConnectedDevices(state: AppState) {
        binding.connectedDevicesContainer.removeAllViews()
        val labels = LabelStore.getLabels(this)

        if (state.connectedDevices.isEmpty()) {
            binding.connectedDevicesContainer.addView(
                buildEmptyPanel(
                    title = "No connected sensors",
                    subtitle = "After a device is connected, its label controls and disconnect action show up here.",
                ),
            )
            return
        }

        state.connectedDevices.forEachIndexed { index, device ->
            val address = device.address
            val activeAnnotation = state.activeAnnotations[address]
            val canLabel = state.isRecording && activeAnnotation == null

            val card = buildDashboardCard().apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                ).also { params ->
                    if (index > 0) params.topMargin = dp(12)
                }
            }
            val content = buildCardColumn()

            val headerRow = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
            }
            val titleColumn = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            }
            titleColumn.addView(
                TextView(this).apply {
                    text = device.name
                    setTextColor(color(R.color.dashboard_text_primary))
                    setTypeface(null, Typeface.BOLD)
                    setTextSize(TypedValue.COMPLEX_UNIT_SP, 17f)
                },
            )
            titleColumn.addView(
                TextView(this).apply {
                    text = address
                    setTextColor(color(R.color.dashboard_text_secondary))
                    setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
                },
            )
            headerRow.addView(titleColumn)
            headerRow.addView(
                MaterialButton(
                    this,
                    null,
                    com.google.android.material.R.attr.materialButtonOutlinedStyle,
                ).apply {
                    text = getString(R.string.disconnect)
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    )
                    strokeColor = ColorStateList.valueOf(color(R.color.dashboard_card_border))
                    setTextColor(color(R.color.dashboard_text_primary))
                    cornerRadius = dp(16)
                    setOnClickListener { bleService?.disconnect(address) }
                },
            )
            content.addView(headerRow)

            content.addView(
                buildInfoPill(
                    text = if (activeAnnotation != null) {
                        "Labeling ${activeAnnotation.label}  #${activeAnnotation.segmentId}"
                    } else {
                        if (state.isRecording) "Ready to label" else "Connect and start recording to label"
                    },
                    backgroundColor = if (activeAnnotation != null) {
                        color(R.color.dashboard_success_soft)
                    } else {
                        color(R.color.dashboard_accent_soft)
                    },
                    textColor = if (activeAnnotation != null) {
                        color(R.color.dashboard_success)
                    } else {
                        color(R.color.dashboard_accent)
                    },
                ).apply {
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    ).also { params -> params.topMargin = dp(14) }
                },
            )

            val chipGroup = ChipGroup(this).apply {
                isSingleLine = false
                chipSpacingHorizontal = dp(8)
                chipSpacingVertical = dp(8)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                ).also { params -> params.topMargin = dp(14) }
            }
            labels.forEach { label ->
                chipGroup.addView(
                    buildLabelChip(label = label, enabled = canLabel) {
                        bleService?.startAnnotation(address, label)
                    },
                )
            }
            content.addView(chipGroup)

            content.addView(
                MaterialButton(
                    this,
                    null,
                    com.google.android.material.R.attr.materialButtonOutlinedStyle,
                ).apply {
                    text = getString(R.string.stop_annotation)
                    isEnabled = state.isRecording && activeAnnotation != null
                    strokeColor = ColorStateList.valueOf(color(R.color.dashboard_card_border))
                    setTextColor(color(R.color.dashboard_text_primary))
                    cornerRadius = dp(16)
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    ).also { params -> params.topMargin = dp(14) }
                    setOnClickListener { bleService?.stopAnnotation(address) }
                },
            )

            card.addView(content)
            binding.connectedDevicesContainer.addView(card)
        }
    }

    private fun refreshButtons() {
        val serviceReady = bleService != null
        val connectedCount = currentState.connectedDevices.size
        binding.scanButton.isEnabled = serviceReady && !currentState.isScanning
        binding.deviceSpinner.isEnabled =
            serviceReady && currentState.devices.isNotEmpty() && connectedCount < BleImuManager.MAX_CONNECTIONS
        binding.connectButton.isEnabled =
            serviceReady && currentState.devices.isNotEmpty() && connectedCount < BleImuManager.MAX_CONNECTIONS
        binding.startRecordingButton.isEnabled = serviceReady && currentState.isConnected && !currentState.isRecording
        binding.stopRecordingButton.isEnabled = serviceReady && currentState.isRecording
        binding.shareButton.isEnabled = !currentState.isRecording && !currentState.lastSavedPath.isNullOrBlank()
    }

    private fun showEditLabelsDialog() {
        val labels = LabelStore.getLabels(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            val padding = dp(18)
            setPadding(padding, padding, padding, padding)
        }
        val labelContainer = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }

        fun rebuildRows() {
            labelContainer.removeAllViews()
            labels.forEachIndexed { index, label ->
                val row = LinearLayout(this).apply {
                    orientation = LinearLayout.HORIZONTAL
                    gravity = Gravity.CENTER_VERTICAL
                    background = roundedBackground(
                        fillColor = color(R.color.dashboard_card_surface_alt),
                        strokeColor = color(R.color.dashboard_card_border),
                        radiusDp = 18,
                    )
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    ).also { params ->
                        if (index > 0) params.topMargin = dp(8)
                    }
                    setPadding(dp(14), dp(12), dp(14), dp(12))
                }
                row.addView(
                    TextView(this).apply {
                        text = label
                        setTextColor(color(R.color.dashboard_text_primary))
                        setTypeface(null, Typeface.BOLD)
                        setTextSize(TypedValue.COMPLEX_UNIT_SP, 15f)
                        layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                    },
                )
                row.addView(
                    MaterialButton(
                        this,
                        null,
                        com.google.android.material.R.attr.materialButtonOutlinedStyle,
                    ).apply {
                        text = "Remove"
                        strokeColor = ColorStateList.valueOf(color(R.color.dashboard_card_border))
                        setTextColor(color(R.color.dashboard_text_primary))
                        cornerRadius = dp(14)
                        setOnClickListener {
                            labels.removeAt(index)
                            rebuildRows()
                        }
                    },
                )
                labelContainer.addView(row)
            }
        }
        rebuildRows()

        val scrollView = ScrollView(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                dp(220),
            )
            addView(labelContainer)
        }
        val inputRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT,
            ).also { params -> params.topMargin = dp(14) }
        }
        val input = EditText(this).apply {
            hint = getString(R.string.edit_labels_add_hint)
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
            maxLines = 1
            background = roundedBackground(
                fillColor = color(R.color.dashboard_card_surface_alt),
                strokeColor = color(R.color.dashboard_card_border),
                radiusDp = 18,
            )
            setPadding(dp(14), dp(12), dp(14), dp(12))
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        inputRow.addView(input)
        inputRow.addView(
            MaterialButton(this).apply {
                text = getString(R.string.edit_labels_add_button)
                cornerRadius = dp(16)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                ).also { params -> params.marginStart = dp(10) }
                setOnClickListener {
                    val newLabel = input.text.toString()
                        .trim()
                        .replace(',', ' ')
                        .replace('\n', ' ')
                        .trim()
                    if (newLabel.isNotBlank() && !labels.contains(newLabel)) {
                        labels.add(newLabel)
                        input.text.clear()
                        rebuildRows()
                    }
                }
            },
        )

        root.addView(scrollView)
        root.addView(inputRow)

        AlertDialog.Builder(this)
            .setTitle(R.string.edit_labels_dialog_title)
            .setView(root)
            .setPositiveButton(R.string.edit_labels_save) { _, _ ->
                LabelStore.saveLabels(this, labels)
                lastRenderedConnectedDevices = emptyList()
                renderState(currentState)
            }
            .setNegativeButton(R.string.edit_labels_cancel, null)
            .show()
    }

    private fun startScan() {
        val service = bleService ?: return
        if (!service.isBluetoothEnabled()) {
            showToast("Turn on Bluetooth first.")
            return
        }
        if (!ensureForegroundServiceStarted()) return
        service.startScan()
    }

    private fun connectSelectedDevice() {
        val service = bleService ?: return
        if (!service.isBluetoothEnabled()) {
            showToast("Turn on Bluetooth first.")
            return
        }
        if (!ensureForegroundServiceStarted()) return
        val selectedIndex = binding.deviceSpinner.selectedItemPosition
        val selectedDevice = currentState.devices.getOrNull(selectedIndex)
        if (selectedDevice == null) {
            showToast("Select a discovered device first.")
            return
        }
        if (currentState.connectedDevices.any { it.address == selectedDevice.address }) {
            showToast("Already connected to ${selectedDevice.name}.")
            return
        }
        service.connect(selectedDevice.address)
    }

    private fun ensureRuntimePermissions(action: PendingAction): Boolean {
        val missing = requiredPermissions().filterNot(::hasPermission)
        if (missing.isEmpty()) {
            pendingAction = PendingAction.NONE
            return true
        }
        pendingAction = action
        permissionLauncher.launch(missing.toTypedArray())
        return false
    }

    private fun requiredPermissions(): List<String> {
        val permissions = mutableListOf(Manifest.permission.ACCESS_FINE_LOCATION)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            permissions += Manifest.permission.BLUETOOTH_SCAN
            permissions += Manifest.permission.BLUETOOTH_CONNECT
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions += Manifest.permission.POST_NOTIFICATIONS
        }
        return permissions
    }

    private fun hasPermission(permission: String): Boolean =
        ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED

    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun startRecording() {
        if (!ensureForegroundServiceStarted()) return
        bleService?.startRecording()
    }

    private fun shareLastFile() {
        val path = currentState.lastSavedPath
        if (path.isNullOrBlank()) {
            showToast("No saved CSV file is available yet.")
            return
        }
        val file = File(path)
        if (!file.exists()) {
            showToast("The last saved file could not be found.")
            return
        }
        val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", file)
        startActivity(
            Intent.createChooser(
                Intent(Intent.ACTION_SEND).apply {
                    type = "text/csv"
                    putExtra(Intent.EXTRA_STREAM, uri)
                    putExtra(Intent.EXTRA_SUBJECT, file.name)
                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                },
                "Share IMU CSV",
            ),
        )
    }

    private fun buildDashboardCard(): MaterialCardView =
        MaterialCardView(this).apply {
            radius = dpFloat(24)
            cardElevation = 0f
            strokeWidth = dp(1)
            setStrokeColor(color(R.color.dashboard_card_border))
            setCardBackgroundColor(color(R.color.dashboard_card_surface))
        }

    private fun buildCardColumn(): LinearLayout =
        LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(18), dp(18), dp(18))
        }

    private fun buildMetricPanel(title: String, value: String, valueTag: String): View =
        LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = roundedBackground(
                fillColor = color(R.color.dashboard_card_surface_alt),
                strokeColor = color(R.color.dashboard_card_border),
                radiusDp = 20,
            )
            setPadding(dp(14), dp(14), dp(14), dp(14))

            addView(
                TextView(this@MainActivity).apply {
                    text = title
                    setTextColor(color(R.color.dashboard_text_secondary))
                    setTypeface(null, Typeface.BOLD)
                    setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
                    letterSpacing = 0.04f
                },
            )
            addView(
                TextView(this@MainActivity).apply {
                    tag = valueTag
                    text = value
                    setTextColor(color(R.color.dashboard_text_primary))
                    setTextSize(TypedValue.COMPLEX_UNIT_SP, 15f)
                    setTypeface(null, Typeface.BOLD)
                    setLineSpacing(0f, 1.15f)
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    ).also { params -> params.topMargin = dp(8) }
                },
            )
        }

    private fun buildInfoPill(
        text: String,
        backgroundColor: Int,
        textColor: Int,
        tag: String? = null,
    ): TextView =
        TextView(this).apply {
            this.tag = tag
            this.text = text
            setTextColor(textColor)
            setTypeface(null, Typeface.BOLD)
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
            background = roundedBackground(
                fillColor = backgroundColor,
                strokeColor = backgroundColor,
                radiusDp = 999,
            )
            setPadding(dp(12), dp(8), dp(12), dp(8))
        }

    private fun buildLabelChip(label: String, enabled: Boolean, onClick: () -> Unit): Chip =
        Chip(this).apply {
            text = label
            isClickable = true
            isCheckable = false
            isEnabled = enabled
            chipBackgroundColor = ColorStateList.valueOf(
                if (enabled) color(R.color.dashboard_accent_soft) else color(R.color.dashboard_card_surface_alt),
            )
            setTextColor(
                if (enabled) color(R.color.dashboard_accent) else color(R.color.dashboard_text_secondary),
            )
            chipStrokeWidth = 0f
            chipMinHeight = dpFloat(38)
            setOnClickListener { onClick() }
        }

    private fun buildEmptyPanel(title: String, subtitle: String): View =
        LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = roundedBackground(
                fillColor = color(R.color.dashboard_card_surface_alt),
                strokeColor = color(R.color.dashboard_card_border),
                radiusDp = 22,
            )
            setPadding(dp(18), dp(18), dp(18), dp(18))

            addView(
                TextView(this@MainActivity).apply {
                    text = title
                    setTextColor(color(R.color.dashboard_text_primary))
                    setTypeface(null, Typeface.BOLD)
                    setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
                },
            )
            addView(
                TextView(this@MainActivity).apply {
                    text = subtitle
                    setTextColor(color(R.color.dashboard_text_secondary))
                    setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                    ).also { params -> params.topMargin = dp(6) }
                },
            )
        }

    private fun roundedBackground(fillColor: Int, strokeColor: Int, radiusDp: Int): GradientDrawable =
        GradientDrawable().apply {
            shape = GradientDrawable.RECTANGLE
            cornerRadius = dpFloat(radiusDp)
            setColor(fillColor)
            setStroke(dp(1), strokeColor)
        }

    private fun color(@ColorRes resId: Int): Int = ContextCompat.getColor(this, resId)

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    private fun dpFloat(value: Int): Float = value * resources.displayMetrics.density

    private fun format(value: Float): String = String.format(Locale.US, "%.2f", value)

    private fun ensureForegroundServiceStarted(): Boolean = try {
        ContextCompat.startForegroundService(this, Intent(this, BleForegroundService::class.java))
        true
    } catch (error: Exception) {
        showToast("Unable to start background service: ${error.message}")
        false
    }

    private enum class PendingAction {
        NONE,
        SCAN,
        CONNECT,
        RECORD,
    }
}
