# pyPSSus
## [简介](#introduction) 
pyPSSus是一款用于管理进程和窗口的Python软件。它具有以下主要功能:
- 创建虚拟桌面,以隔离进程和窗口 
- 挂起/恢复进程,移动窗口到不同虚拟桌面 
- 定期扫描并管理所有运行的进程 
- 检测当前活动窗口和前景窗口的变化
- 管理系统托盘中的应用程序
## [依赖](#dependencies) 
pyPSSus依赖于以下Python库:
- psutil - 用于获取进程和系统信息 
- win32api - 用于与Windows API交互 
- win32gui - 用于枚举和操作窗口
- pyvda - 用于管理Windows 10的虚拟桌面
## [使用](#usage) 
1. 确保安装所有依赖库 
2. 下载main.py文件 
3. 运行main.py启动程序 
4. 可选:调整定时器间隔(TIMER_INTERVAL)和虚拟桌面名称(ICEBOX_NAME) 
5. 创建“icebox”虚拟桌面后,将窗口拖拽到该桌面将自动挂起关联进程 
6. 恢复窗口将自动恢复关联进程 
7. “susoend system tray applications”选项可以选择是否挂起系统托盘应用 
8. 将鼠标悬停在窗口标题栏上方可以显示用于挂起该窗口系统托盘应用的菜单 
9. 程序运行后会定期扫描和管理窗口和进程
## [联系](#contact) 
如果有任何问题或建议,欢迎联系我!我的邮箱是:di.zang@ustc.edu
## Introduction 
pyPSSus is a Python software for managing processes and windows. It has the following main features: 
- Create virtual desktops to isolate processes and windows
- Suspend/resume processes and move windows to different virtual desktops 
- Periodically scan and manage all running processes
- Detect changes in the active window and foreground window
- Manage applications in the system tray
## [Dependencies](#dependencies)
pyPSSus depends on the following Python libraries:
- psutil - For getting process and system information
- win32api - For interacting with the Windows API
- win32gui - For enumerating and manipulating windows
- pyvda - For managing virtual desktops on Windows 10
## [Usage](#usage)
1. Make sure all dependencies are installed 
2. Download the main.py file 
3. Run main.py to launch the program  
4. Optional: Adjust the timer interval (TIMER_INTERVAL) and virtual desktop name (ICEBOX_NAME) 
5. After creating the "icebox" virtual desktop, dragging windows to that desktop will automatically suspend the associated processes  
6. Restoring windows will automatically resume the associated processes 
7. The "suspend system tray applications" option can be selected to suspend system tray apps 
8. Hovering the mouse over a window's title bar will show a menu to suspend that window's system tray apps 
9. The program will periodically scan and manage windows and processes after running
## [Contact](#contact)
If you have any questions or suggestions, feel free to contact me! My email is: di.zang@ustc.edu 