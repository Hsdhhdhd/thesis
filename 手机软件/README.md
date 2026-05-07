# BLE IMU Android Receiver

This is a native Android app for receiving IMU notifications from the existing
`ble-imu-sensor` firmware and saving the data to CSV on a phone.

## What it does

- Scans for BLE peripherals named `ble-imu-sensor`
- Connects to the existing custom IMU characteristic
- Parses the same 12-byte payload used by the desktop receiver
- Displays live acceleration and gyroscope values
- Captures the phone's location while recording, preferring satellite GPS and
  falling back to the latest available network location when no fresh GPS fix is
  available
- Lets you mark labeled time ranges such as `scooter` or `lunch` while recording
- Records incoming packets to CSV
- Runs a foreground service so collection can continue with the screen off or
  while the app is in the background
- Automatically reconnects to the last BLE IMU device after an unexpected drop
- Shares the last saved CSV file through Android's standard share sheet

## BLE protocol

- Service UUID: `12345678-1234-5678-1234-56789abcdef0`
- Characteristic UUID: `12345678-1234-5678-1234-56789abcdef1`
- Payload format: 6 little-endian signed `int16` values
  - `accel_x`, `accel_y`, `accel_z`
  - `gyro_x`, `gyro_y`, `gyro_z`

The app uses the same unit conversion as the desktop receiver:

- Acceleration: `raw / 1000.0` -> `m/s^2`
- Gyroscope: `raw * 0.0572957795` -> `deg/s`

## Output files

Recorded files are written to the app's external documents directory:

`Android/data/com.l1172.bleimuandroid/files/Documents/BleImu/`

Each file is named like:

`imu_data_20260319_153000.csv`

## Build

1. Open `android_receiver/` in Android Studio
2. Let Android Studio install the required Android SDK / Gradle components
3. Build and run on an Android phone with BLE enabled

## Release APK

- A signed release APK can be built with `.\gradlew.bat assembleRelease`
- The release package is generated at:
  `app/build/outputs/apk/release/app-release.apk`
- Keep both `keystore.properties` and the `.jks` signing file backed up. You need
  them again for future updates of the same app package.

## Google Play Bundle

- A Google Play upload bundle can be built with `.\gradlew.bat bundleRelease`
- The upload bundle is generated at:
  `app/build/outputs/bundle/release/app-release.aab`
- A 512x512 Play Console icon file is generated at:
  `store_assets/google-play-icon-512.png`

Recommended environment:

- Android Studio Ladybug or newer
- JDK 17
- Android SDK 35

## Permissions

The app requests:

- `BLUETOOTH_SCAN`
- `BLUETOOTH_CONNECT`
- `ACCESS_FINE_LOCATION`
- `POST_NOTIFICATIONS`
- `FOREGROUND_SERVICE`
- `FOREGROUND_SERVICE_CONNECTED_DEVICE`
- `FOREGROUND_SERVICE_LOCATION`

## Background behavior

- the app starts a foreground service and keeps an ongoing notification visible
- BLE collection can continue when the phone is locked or the app is not on
  screen
- recording stops automatically if the BLE connection closes
