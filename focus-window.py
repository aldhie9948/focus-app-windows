import os
import re 
import time 
import ctypes 
import win32gui
import win32con
import win32api
import win32com.client

# --- Konfigurasi ---
IDLE_THRESHOLD_SECONDS = 5
CHECK_INTERVAL_SECONDS = 2


def get_idle_duration():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]

    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(lii)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        millis = win32api.GetTickCount() - lii.dwTime
        return millis / 1000.0
    return 0


def get_matching_windows(regex):
    matching = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if regex.search(title):
                matching.append((hwnd, title))

    win32gui.EnumWindows(callback, None)
    return matching



def is_window_focused(hwnd:int):
    return hwnd == win32gui.GetForegroundWindow()

def focus_window(hwnd:int):
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys("%")
    win32gui.SetForegroundWindow(hwnd)

def main():
    pattern = input("Masukkan regex window title yang ingin difokuskan: ").strip()
    print(f"Watching for window matching: {pattern}")
    regex = re.compile(pattern, re.IGNORECASE)

    while True:
        windows = get_matching_windows(regex)
        for hwnd, title in windows:
            if not is_window_focused(hwnd):
                idle = get_idle_duration()
                print(f"[{title}] not focused. Idle: {idle:.2f}s")
                if idle >= IDLE_THRESHOLD_SECONDS:
                    print(f"→ Focusing: {title}")
                    focus_window(hwnd)
                else:
                    print("→ User is active. Skip.")
            else:
                print(f"[{title}] already focused.")
        time.sleep(CHECK_INTERVAL_SECONDS)  # delay 2 detik antar pengecekan
        os.system("cls") # clear terminal


if __name__ == "__main__":
  main()

