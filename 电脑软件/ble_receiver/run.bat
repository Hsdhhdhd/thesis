@echo off
setlocal

echo 检查 Python...
py -3 --version >nul 2>&1 || (
	echo 未检测到可用的 Python，請先安裝 Python 3 並勾選 "Add python.exe to PATH"。
	pause
	exit /b 1
)

echo 安装依赖...
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt

echo.
echo 启动 BLE IMU 接收器...
py -3 imu_receiver_gui.py

pause
endlocal
