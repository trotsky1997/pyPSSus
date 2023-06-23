# 导入所需的模块
import contextlib
import threading
import time

import psutil
import win32api
import win32gui
import win32process
from pyvda import AppView, VirtualDesktop

# 定义一些常量和变量
ICEBOX_NAME = "icebox"  # 虚拟桌面的名称
TIMER_INTERVAL = 15  # 定时器的间隔（秒）
icebox_id = None  # 虚拟桌面的编号
icebox = None  # 虚拟桌面的编号
suspended_windows = {}  # 存储被挂起的窗口句柄和进程 ID 的字典
timer = None  # 定时器对象


# 定义一些辅助函数
def create_icebox():
    # 创建一个名为 icebox 的虚拟桌面，并返回它的编号
    global icebox, icebox_id
    icebox = VirtualDesktop.create()
    icebox.rename(ICEBOX_NAME)
    icebox_id = icebox.id
    return icebox_id


def get_hwnds_by_pid(pid):
    hwnds = []

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True

    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def get_window_info_by_hwnd(hwnd):
    """
    Given an HWND, returns the process ID, window title, and virtual desktop ID (if available).

    :param hwnd: An integer representing the HWND (window handle).
    :return: A tuple containing the process ID (int), window title (str), and virtual desktop ID (str or None).
    """
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    title = win32gui.GetWindowText(hwnd)
    try:
        vdid = AppView(hwnd).desktop_id
    except Exception:
        vdid = None
    return pid, title, vdid


def get_forewindow():
    return win32gui.GetForegroundWindow()


def get_all_windows():
    """
    Returns a dictionary containing all the windows that are currently open in the system.
    The keys are the window handles (hwnd) and the values are the process IDs (pid).
    This function does this by enumerating all the windows and collecting the visible ones.

    Parameters:
    None

    Returns:
    A dictionary where keys are window handles (hwnd) and values are process IDs and title (pid,title).
    """

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            hwnds[hwnd] = get_window_info_by_hwnd(hwnd)
        return True

    hwnds = {}
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def suspend_process(pid):
    # 挂起一个进程，并返回它的状态
    process = psutil.Process(pid)
    forepid = get_window_info_by_hwnd(get_forewindow())[0]
    if pid not in suspended_windows.values() or pid == forepid:  # 如果是当前活动窗口，则不冻结
        print(f"{pid}是当前活动窗口，不可挂起")
        if process.status() == "stopped":
            resume_process(pid)
        return process.status()
    if process.status() == "stopped":
        return process.status()
    print(f"准备挂起{pid}")
    process.suspend()
    print(f"挂起了进程{pid}")
    return process.status()


def resume_process(pid):
    # 恢复一个进程，并返回它的状态
    process = psutil.Process(pid)
    print(f"准备恢复进程{pid}")
    process.resume()
    print(f"恢复了进程{pid}")
    return process.status()


def start_timer():
    # 启动一个定时器，并返回它
    global timer
    timer = win32api.SetTimer(None, None, TIMER_INTERVAL * 1000, timer_callback)
    return timer


def stop_timer():
    # 停止一个定时器，并返回它
    global timer
    win32api.KillTimer(None, timer)
    timer = None
    return timer


# 定义一些回调函数
def timer_callback(hwnd, msg, idEvent, time):
    # 在定时器到期时执行的函数
    run_func_in_new_thread(process_scan)


def global_timer_callback(hwnd, msg, idEvent, time):
    # 定期扫描所有进程并挂起或恢复对应的进程
    run_func_in_new_thread(process_scan)


def hook_callback(event=None):
    # 在钩子事件发生时执行的函数
    global suspended_windows, timer
    run_func_in_new_thread(check_forewindow)
    run_func_in_new_thread(process_scan)
    # event_type = wParam # 事件类型，如鼠标左键按下、释放等
    # event_data = lParam # 事件数据，如鼠标坐标、键盘扫描码等

    # 根据事件类型和数据执行相应的操作，如取消定时器、恢复或挂起进程等
    return 0


# 主程序开始

# 创建 icebox 虚拟桌面，并获取它的编号
icebox_id = create_icebox()


def process_scan():
    # 遍历所有正在运行的进程，并获取它们的窗口句柄和进程 ID
    for hwnd, proc_info in get_all_windows().items():
        with contextlib.suppress(
            psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess
        ):
            pid, title, desktop_id = proc_info
            if hwnd != 0:
                if desktop_id == icebox_id:
                    # print(f"Process {pid} has window handle {hwnd} with title {title} in virtual desktop {desktop_id,icebox_id}")
                    # 如果窗口在 icebox 内，挂起进程，并将其添加到字典中
                    suspended_windows[hwnd] = pid
                    suspend_process(pid)
                elif hwnd in suspended_windows:
                    # 如果在字典中，则恢复进程，并将其从字典中删除
                    resume_process(pid)
                    suspended_windows.pop(hwnd)
    for proc in psutil.process_iter():
        if proc.status() == "stopped" and proc.pid not in suspended_windows.values():
            hwnds = get_hwnds_by_pid(proc.pid)
            if hwnds != [] and all(hwnd not in suspended_windows for hwnd in hwnds):
                for hwnd in hwnds:
                    if get_window_info_by_hwnd(hwnd)[2] == icebox_id:
                        suspended_windows[hwnd] = pid


def run_func_in_new_thread(target):
    # 在一个新线程中运行函数
    threading.Thread(target=target).start()


def check_forewindow():
    # 获取当前活动的窗口句柄，并检查它是否在字典中
    foreground_window = win32gui.GetForegroundWindow()
    if foreground_window in suspended_windows:
        # 如果是，恢复对应的进程，并启动一个定时器
        pid = suspended_windows[foreground_window]
        resume_process(pid)
        start_timer()


run_func_in_new_thread(process_scan)
old_forewindow_handle = None


def main_loop():
    global old_forewindow_handle
    while True:
        time.sleep(0.3)
        foreground_window = win32gui.GetForegroundWindow()
        if (
            foreground_window != old_forewindow_handle
            or foreground_window in suspended_windows
        ):
            old_forewindow_handle = foreground_window
            # print(foreground_window,get_window_info_by_hwnd(foreground_window))
            hook_callback()


main_loop()
