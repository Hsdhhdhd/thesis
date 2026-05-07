#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BLE IMU 接收器 - 简化版 GUI"""

import sys
import asyncio
import struct
from datetime import datetime
from collections import deque
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QComboBox, QGroupBox, QGridLayout,
    QCheckBox, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QFont
import bleak
from bleak import BleakClient, BleakScanner


IMU_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
IMU_DATA_CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"


class IMUDataBuffer:
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.data_list = deque(maxlen=max_size)

    def add(self, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, timestamp):
        self.data_list.append({
            'timestamp': timestamp,
            'accel_x': accel_x,
            'accel_y': accel_y,
            'accel_z': accel_z,
            'gyro_x': gyro_x,
            'gyro_y': gyro_y,
            'gyro_z': gyro_z,
        })

    def clear(self):
        self.data_list.clear()

    def get_all(self):
        return list(self.data_list)


class BLEThread(QThread):
    device_found = pyqtSignal(str, str)
    connected = pyqtSignal(bool, str)
    data_received = pyqtSignal(dict)
    disconnected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.scan_mode = False
        self.connect_mode = False
        self.device_address = None
        self.running = True

    def run(self):
        if self.scan_mode:
            asyncio.run(self.scan_devices())
        elif self.connect_mode:
            asyncio.run(self.connect_device())

    async def scan_devices(self):
        self.device_found.emit("扫描中...", "")
        try:
            devices = await BleakScanner.discover()
            for device in devices:
                self.device_found.emit(device.name or "Unknown", device.address)
        except Exception as e:
            self.device_found.emit(f"扫描失败: {str(e)}", "")
        # 发送扫描完成信号
        self.device_found.emit("扫描完成", "")

    async def connect_device(self):
        try:
            async with BleakClient(self.device_address) as client:
                if client.is_connected:  # 改为属性而不是方法
                    self.connected.emit(True, f"已连接到 {self.device_address}")

                    def notification_handler(sender, data):
                        if len(data) >= 12:
                            values = struct.unpack('<hhhhhh', data[:12])
                            imu_data = {
                                'accel_x': values[0],
                                'accel_y': values[1],
                                'accel_z': values[2],
                                'gyro_x': values[3],
                                'gyro_y': values[4],
                                'gyro_z': values[5],
                                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            }
                            self.data_received.emit(imu_data)

                    await client.start_notify(IMU_DATA_CHAR_UUID, notification_handler)
                    while self.connect_mode and self.running:
                        await asyncio.sleep(0.1)
                    await client.stop_notify(IMU_DATA_CHAR_UUID)
                else:
                    self.connected.emit(False, "连接失败")
        except Exception as e:
            self.connected.emit(False, f"连接错误: {str(e)}")
            self.disconnected.emit()

    def stop(self):
        self.running = False
        self.scan_mode = False
        self.connect_mode = False


class IMUReceiverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLE IMU 数据接收器")
        self.setGeometry(100, 100, 1200, 700)
        self.ble_thread = None
        self.data_buffer = IMUDataBuffer()
        self.data_file = None
        self.is_recording = False
        self.packet_count = 0
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()

        # 左侧
        left_layout = QVBoxLayout()

        # 连接控制
        control_group = QGroupBox("连接控制")
        control_layout = QGridLayout()
        self.device_combo = QComboBox()
        control_layout.addWidget(QLabel("设备列表:"), 0, 0)
        control_layout.addWidget(self.device_combo, 0, 1)

        self.scan_btn = QPushButton("扫描设备")
        self.scan_btn.clicked.connect(self.scan_devices)
        control_layout.addWidget(self.scan_btn, 1, 0)

        self.connect_btn = QPushButton("连接设备")
        self.connect_btn.clicked.connect(self.connect_device)
        self.connect_btn.setEnabled(False)
        control_layout.addWidget(self.connect_btn, 1, 1)

        self.disconnect_btn = QPushButton("断开连接")
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        self.disconnect_btn.setEnabled(False)
        control_layout.addWidget(self.disconnect_btn, 2, 0, 1, 2)

        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)

        # 数据显示
        display_group = QGroupBox("实时数据")
        display_layout = QGridLayout()

        accel_font = QFont()
        accel_font.setPointSize(12)
        accel_font.setBold(True)

        display_layout.addWidget(QLabel("加速度 (m/s²)"), 0, 0, 1, 3)
        self.accel_x_label = QLabel("X: 0")
        self.accel_x_label.setFont(accel_font)
        self.accel_x_label.setStyleSheet("color: red;")
        self.accel_y_label = QLabel("Y: 0")
        self.accel_y_label.setFont(accel_font)
        self.accel_y_label.setStyleSheet("color: green;")
        self.accel_z_label = QLabel("Z: 0")
        self.accel_z_label.setFont(accel_font)
        self.accel_z_label.setStyleSheet("color: blue;")
        
        display_layout.addWidget(self.accel_x_label, 1, 0)
        display_layout.addWidget(self.accel_y_label, 1, 1)
        display_layout.addWidget(self.accel_z_label, 1, 2)

        display_layout.addWidget(QLabel("角速度 (°/s)"), 2, 0, 1, 3)
        self.gyro_x_label = QLabel("X: 0")
        self.gyro_x_label.setFont(accel_font)
        self.gyro_x_label.setStyleSheet("color: red;")
        self.gyro_y_label = QLabel("Y: 0")
        self.gyro_y_label.setFont(accel_font)
        self.gyro_y_label.setStyleSheet("color: green;")
        self.gyro_z_label = QLabel("Z: 0")
        self.gyro_z_label.setFont(accel_font)
        self.gyro_z_label.setStyleSheet("color: blue;")
        
        display_layout.addWidget(self.gyro_x_label, 3, 0)
        display_layout.addWidget(self.gyro_y_label, 3, 1)
        display_layout.addWidget(self.gyro_z_label, 3, 2)

        display_layout.addWidget(QLabel("时间戳:"), 4, 0)
        self.timestamp_label = QLabel("--:--:--.---")
        self.timestamp_label.setFont(accel_font)
        display_layout.addWidget(self.timestamp_label, 4, 1, 1, 2)

        display_layout.addWidget(QLabel("接收数据包:"), 5, 0)
        self.packet_count_label = QLabel("0")
        self.packet_count_label.setFont(accel_font)
        display_layout.addWidget(self.packet_count_label, 5, 1, 1, 2)

        display_group.setLayout(display_layout)
        left_layout.addWidget(display_group)

        # 数据记录
        record_group = QGroupBox("数据记录")
        record_layout = QGridLayout()

        self.record_checkbox = QCheckBox("启用自动记录")
        self.record_checkbox.stateChanged.connect(self.toggle_recording)
        self.record_checkbox.setEnabled(False)
        record_layout.addWidget(self.record_checkbox, 0, 0, 1, 2)

        self.save_btn = QPushButton("保存数据")
        self.save_btn.clicked.connect(self.save_data)
        self.save_btn.setEnabled(False)
        record_layout.addWidget(self.save_btn, 1, 0, 1, 2)

        self.clear_btn = QPushButton("清除数据")
        self.clear_btn.clicked.connect(self.clear_data)
        record_layout.addWidget(self.clear_btn, 2, 0, 1, 2)

        record_group.setLayout(record_layout)
        left_layout.addWidget(record_group)

        # 状态信息
        info_group = QGroupBox("状态信息")
        info_layout = QVBoxLayout()
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.status_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        info_layout.addWidget(self.log_text)

        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)
        left_layout.addStretch()

        # 右侧：数据表格
        right_layout = QVBoxLayout()

        table_group = QGroupBox("数据历史")
        table_layout = QVBoxLayout()

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(7)
        self.data_table.setHorizontalHeaderLabels(["时间戳", "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z"])
        self.data_table.setMaximumHeight(400)
        table_layout.addWidget(self.data_table)

        table_group.setLayout(table_layout)
        right_layout.addWidget(table_group)

        # 统计信息
        stat_group = QGroupBox("数据统计")
        stat_layout = QGridLayout()

        stat_layout.addWidget(QLabel("加速度范围:"), 0, 0)
        self.accel_range_label = QLabel("X: [--, --]  Y: [--, --]  Z: [--, --]")
        stat_layout.addWidget(self.accel_range_label, 0, 1)

        stat_layout.addWidget(QLabel("角速度范围:"), 1, 0)
        self.gyro_range_label = QLabel("X: [--, --]  Y: [--, --]  Z: [--, --]")
        stat_layout.addWidget(self.gyro_range_label, 1, 1)

        stat_layout.addWidget(QLabel("平均值:"), 2, 0)
        self.avg_label = QLabel("计算中...")
        stat_layout.addWidget(self.avg_label, 2, 1)

        stat_group.setLayout(stat_layout)
        right_layout.addWidget(stat_group)
        right_layout.addStretch()

        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 1)
        central_widget.setLayout(layout)

    def scan_devices(self):
        self.scan_btn.setEnabled(False)
        self.device_combo.clear()
        self.device_combo.addItem("扫描中...")
        self.log("开始扫描设备...")

        self.ble_thread = BLEThread()
        self.ble_thread.device_found.connect(self.on_device_found)
        self.ble_thread.scan_mode = True
        self.ble_thread.start()

    def on_device_found(self, name, address):
        if "扫描中" in name:
            self.device_combo.clear()
        elif "扫描完成" in name:
            self.scan_btn.setEnabled(True)
            if self.device_combo.count() > 0:
                self.connect_btn.setEnabled(True)
            self.log("扫描完成，现在可以连接")
        else:
            self.log(f"发现设备: {name} ({address})")
            self.device_combo.addItem(f"{name or 'Unknown'}", address)

    def connect_device(self):
        if self.device_combo.count() == 0:
            QMessageBox.warning(self, "错误", "请先扫描设备")
            return

        device_address = self.device_combo.currentData()
        device_name = self.device_combo.currentText()

        if not device_address:
            QMessageBox.warning(self, "错误", "请选择有效的设备")
            return

        self.connect_btn.setEnabled(False)
        self.scan_btn.setEnabled(False)
        self.log(f"正在连接 {device_name}...")

        self.ble_thread = BLEThread()
        self.ble_thread.connected.connect(self.on_connected)
        self.ble_thread.data_received.connect(self.on_data_received)
        self.ble_thread.disconnected.connect(self.on_disconnected)
        self.ble_thread.device_address = device_address
        self.ble_thread.connect_mode = True
        self.ble_thread.start()

    def on_connected(self, success, message):
        self.log(message)
        if success:
            self.status_label.setText("已连接 ✓")
            self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
            self.disconnect_btn.setEnabled(True)
            self.record_checkbox.setEnabled(True)
            self.save_btn.setEnabled(True)
        else:
            self.status_label.setText("连接失败 ✗")
            self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
            self.connect_btn.setEnabled(True)
            self.scan_btn.setEnabled(True)

    def on_data_received(self, imu_data):
        self.accel_x_label.setText(f"X: {imu_data['accel_x']}")
        self.accel_y_label.setText(f"Y: {imu_data['accel_y']}")
        self.accel_z_label.setText(f"Z: {imu_data['accel_z']}")
        self.gyro_x_label.setText(f"X: {imu_data['gyro_x']}")
        self.gyro_y_label.setText(f"Y: {imu_data['gyro_y']}")
        self.gyro_z_label.setText(f"Z: {imu_data['gyro_z']}")
        self.timestamp_label.setText(imu_data['timestamp'])

        self.packet_count += 1
        self.packet_count_label.setText(str(self.packet_count))

        self.data_buffer.add(
            imu_data['accel_x'], imu_data['accel_y'], imu_data['accel_z'],
            imu_data['gyro_x'], imu_data['gyro_y'], imu_data['gyro_z'],
            imu_data['timestamp']
        )

        self.update_table()
        self.update_statistics()

        if self.is_recording and self.data_file:
            self.data_file.write(f"{imu_data['timestamp']},{imu_data['accel_x']},{imu_data['accel_y']},"
                                f"{imu_data['accel_z']},{imu_data['gyro_x']},{imu_data['gyro_y']},"
                                f"{imu_data['gyro_z']}\n")

    def update_table(self):
        data_list = self.data_buffer.get_all()
        data_list = list(data_list)[-20:]
        
        self.data_table.setRowCount(len(data_list))
        for row, data in enumerate(data_list):
            self.data_table.setItem(row, 0, QTableWidgetItem(data['timestamp']))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(data['accel_x'])))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(data['accel_y'])))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(data['accel_z'])))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(data['gyro_x'])))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(data['gyro_y'])))
            self.data_table.setItem(row, 6, QTableWidgetItem(str(data['gyro_z'])))

    def update_statistics(self):
        data_list = self.data_buffer.get_all()
        if not data_list:
            return

        accel_x_vals = [d['accel_x'] for d in data_list]
        accel_y_vals = [d['accel_y'] for d in data_list]
        accel_z_vals = [d['accel_z'] for d in data_list]
        gyro_x_vals = [d['gyro_x'] for d in data_list]
        gyro_y_vals = [d['gyro_y'] for d in data_list]
        gyro_z_vals = [d['gyro_z'] for d in data_list]

        accel_range = f"X: [{min(accel_x_vals)}, {max(accel_x_vals)}]  Y: [{min(accel_y_vals)}, {max(accel_y_vals)}]  Z: [{min(accel_z_vals)}, {max(accel_z_vals)}]"
        gyro_range = f"X: [{min(gyro_x_vals)}, {max(gyro_x_vals)}]  Y: [{min(gyro_y_vals)}, {max(gyro_y_vals)}]  Z: [{min(gyro_z_vals)}, {max(gyro_z_vals)}]"

        avg_accel_x = sum(accel_x_vals) / len(accel_x_vals)
        avg_accel_y = sum(accel_y_vals) / len(accel_y_vals)
        avg_accel_z = sum(accel_z_vals) / len(accel_z_vals)
        avg_gyro_x = sum(gyro_x_vals) / len(gyro_x_vals)
        avg_gyro_y = sum(gyro_y_vals) / len(gyro_y_vals)
        avg_gyro_z = sum(gyro_z_vals) / len(gyro_z_vals)

        avg_text = f"Accel: ({avg_accel_x:.1f}, {avg_accel_y:.1f}, {avg_accel_z:.1f})  Gyro: ({avg_gyro_x:.1f}, {avg_gyro_y:.1f}, {avg_gyro_z:.1f})"

        self.accel_range_label.setText(accel_range)
        self.gyro_range_label.setText(gyro_range)
        self.avg_label.setText(avg_text)

    def toggle_recording(self, state):
        if state:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"imu_data_{timestamp}.csv"
            self.data_file = open(filename, 'w')
            self.data_file.write("timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n")
            self.is_recording = True
            self.log(f"开始记录数据: {filename}")
        else:
            if self.data_file:
                self.data_file.close()
            self.is_recording = False
            self.log("停止记录数据")

    def save_data(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存数据", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\n")
                    for data in self.data_buffer.get_all():
                        f.write(f"{data['timestamp']},{data['accel_x']},{data['accel_y']},"
                               f"{data['accel_z']},{data['gyro_x']},{data['gyro_y']},"
                               f"{data['gyro_z']}\n")
                self.log(f"数据已保存: {filename}")
                QMessageBox.information(self, "成功", f"数据已保存到: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def clear_data(self):
        self.data_buffer.clear()
        self.packet_count = 0
        self.packet_count_label.setText("0")
        self.data_table.setRowCount(0)
        self.log("数据已清除")

    def disconnect_device(self):
        if self.ble_thread:
            self.ble_thread.connect_mode = False
            self.ble_thread.stop()

    def on_disconnected(self):
        self.status_label.setText("已断开 ✗")
        self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        self.disconnect_btn.setEnabled(False)
        self.record_checkbox.setEnabled(False)
        self.record_checkbox.setChecked(False)
        self.connect_btn.setEnabled(True)
        self.scan_btn.setEnabled(True)
        self.log("设备连接已断开")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def closeEvent(self, event):
        if self.ble_thread:
            self.ble_thread.stop()
        if self.is_recording and self.data_file:
            self.data_file.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IMUReceiverApp()
    window.show()
    sys.exit(app.exec_())
