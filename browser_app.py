"""Local Windows app hosted in Chrome, sharing the desktop SQLite data."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import urllib.request
import app

URL = 'http://127.0.0.1:8000/'

def configure_storage():
    store=Path(os.getenv('LOCALAPPDATA',str(Path.home()))) / 'SoGiaHan'
    store.mkdir(parents=True,exist_ok=True)
    app.DB=store/'accounts.db'
    app.ROOT=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))

def open_chrome():
    candidates=[]
    if sys.platform=='win32':
        import winreg
        for hive in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(hive,r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe') as key:
                    candidates.append(winreg.QueryValue(key,None))
            except OSError:pass
        for folder in ('PROGRAMFILES','PROGRAMFILES(X86)','LOCALAPPDATA'):
            if os.getenv(folder):candidates.append(str(Path(os.environ[folder])/'Google/Chrome/Application/chrome.exe'))
    for candidate in candidates:
        if Path(candidate).is_file():subprocess.Popen([candidate,URL]);return
    import webbrowser
    webbrowser.open(URL)

def main():
    configure_storage()
    if '--remind' in sys.argv:
        import desktop
        desktop.reminder()
        return
    # No proxy for local health checks; only reuse this app's own listener.
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(URL+'api/health',timeout=2) as r:health=json.load(r)
        if health.get('app')!='so-gia-han':raise ValueError('Cổng 8000 đang được ứng dụng khác sử dụng')
    except (OSError,ValueError):
        try:server=app.ThreadingHTTPServer(('127.0.0.1',8000),app.Handler)
        except OSError:
            import tkinter as tk
            from tkinter import messagebox
            root=tk.Tk();root.withdraw();messagebox.showerror('Không mở được Sổ Gia Hạn','Cổng 8000 đang được dùng. Hãy đóng phiên bản app cũ rồi mở lại.');root.destroy();return
        with app.connect():pass
        if '--serve-only' not in sys.argv:
            threading.Thread(target=open_chrome,daemon=True).start()
        server.serve_forever()
    else:open_chrome()

if __name__=='__main__':main()
