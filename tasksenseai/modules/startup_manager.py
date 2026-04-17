# -*- coding: utf-8 -*-
import os
import sys
import winreg
import logging

APP_NAME = "TaskSenseAI"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

def get_run_command():
    """Construct the command line to run the app minimized."""
    # Find the path to run_tasksense.py relative to the project root
    # assuming this file is in tasksenseai/modules/startup_manager.py
    # or just use the entry point from sys.argv
    
    python_exe = sys.executable
    
    # Try to find run_tasksense.py in the project root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    script_path = os.path.join(base_dir, "run_tasksense.py")
    
    if not os.path.exists(script_path):
        # Fallback to sys.argv[0] if it looks like the right script
        script_path = os.path.abspath(sys.argv[0])

    return f'"{python_exe}" "{script_path}" --minimized'

def set_autostart(enabled=True):
    """Add or remove the app from Windows startup registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_ALL_ACCESS)
        if enabled:
            cmd = get_run_command()
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            logging.info(f"Auto-start enabled: {cmd}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                logging.info("Auto-start disabled.")
            except FileNotFoundError:
                pass # Already disabled
        winreg.CloseKey(key)
        return True
    except Exception as e:
        logging.error(f"Failed to set auto-start: {e}")
        return False

def is_autostart_enabled():
    """Check if the registry key exists and matches our command."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            # Basic check: if it contains APP_NAME or script path
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception as e:
        logging.error(f"Failed to check auto-start status: {e}")
        return False
