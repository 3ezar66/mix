#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KASHIF NC ULTIMATE – Infinite Action Crypto‑Miner Hunter
Classic Norton Commander Style • Unlimited Actions • Modular • Real
"""
import os
import sys
import asyncio
import subprocess
import socket
import ipaddress
import sqlite3
import requests
import time
from datetime import datetime
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import message_dialog

# ====== CONFIG ======
DB_NAME = "kashif_miner_nc.db"
NC_STYLE = Style.from_dict({
    "menu-bar": "bold white bg:#005fff",
    "footer": "black bg:#ffff55",
    "frame.label": "bold white bg:#005fff",
    "body": "white bg:#0000aa",
    "text": "white bg:#0000aa",
    "selected": "bold black bg:#ffff55",
    "highlighted": "bold white bg:#ff9933",
    "alert": "bold red bg:#ffff55",
})

HEADER = [("class:menu-bar", "  F1 Help   F2 Actions   F3 View   F4 Edit   F5 Scan   F6 AI   F7 Tools   F8 Script   F9 Custom   F10 Quit")]
FOOTER = [("class:footer", " Tab: Switch | Enter: Action | F2: Menu | F10/q: Quit | Infinite Real Actions ")]

# ====== DB INIT ======
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS scan_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        ports TEXT,
        method TEXT,
        details TEXT,
        created TEXT
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        result TEXT,
        time TEXT
    )''')
    conn.commit()
    conn.close()

# ====== CORE ACTIONS ======
def scan_ports_range(ip_range, ports):
    results = []
    try:
        start_ip, end_ip = ip_range.split('-')
        curr = ipaddress.IPv4Address(start_ip.strip())
        end = ipaddress.IPv4Address(end_ip.strip())
        while curr <= end:
            ip = str(curr)
            open_ports = []
            for port in ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.4)
                        if s.connect_ex((ip, port)) == 0:
                            open_ports.append(port)
                except Exception:
                    pass
            if open_ports:
                results.append((ip, open_ports))
            curr += 1
        return results
    except Exception as e:
        return [("SCAN ERROR", [str(e)])]

def log_action(action, result):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO logs (action, result, time) VALUES (?, ?, ?)",
              (action, str(result), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def custom_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=20)
        return output.decode(errors='ignore')
    except Exception as e:
        return f"Error: {e}"

def ai_predict(text):
    return f"AI: This is a mock prediction for '{text}'. [Integrate your AI here]"

# ====== PANELS ======
class PanelState:
    def __init__(self):
        self.left_content = "Press F5 to start port scan!\nOr F2 for more actions."
        self.right_content = "Real-time logs:\n"
        self.focus_left = True
        self.selected_action = None

    def update_left(self, text):
        self.left_content = text

    def update_right(self, text):
        self.right_content = text

# ====== APPLICATION ======
def main():
    init_db()
    state = PanelState()

    left_panel = TextArea(
        text=state.left_content,
        style="class:text",
        read_only=True,
        width=44,
        height=20,
        scrollbar=True,
    )
    right_panel = TextArea(
        text=state.right_content,
        style="class:text",
        read_only=True,
        width=44,
        height=20,
        scrollbar=True,
    )

    def refresh():
        left_panel.text = state.left_content
        right_panel.text = state.right_content

    # === KEY BINDINGS ===
    kb = KeyBindings()

    @kb.add("tab")
    def _(event):
        state.focus_left = not state.focus_left
        refresh()

    @kb.add("f10")
    @kb.add("q")
    def _(event):
        event.app.exit()

    @kb.add("f1")
    def _(event):
        message_dialog(
            title="Help",
            text="Classic NC. F5: Scan | F2: Menu | F6: AI | F7: Tools | F8: Script | F9: Custom | Tab: Switch | F10: Quit"
        ).run()

    @kb.add("f2")
    def _(event):
        state.left_content = (
            "Choose action:\n"
            " 1. Full IP Scan\n"
            " 2. Quick Port Scan\n"
            " 3. Show Logs\n"
            " 4. Run Custom Command\n"
            " 5. AI Prediction\n"
            " 6. Real-Time Netstat\n"
            " 7. Exit"
        )
        refresh()
        # Wait for user input
        selection = input("Select menu [1-7]: ").strip()
        if selection == "1":
            ip_range = input("Enter IP range (start-end): ")
            res = scan_ports_range(ip_range, [22, 3333, 4444, 5555])
            state.left_content = "Full Scan Results:\n" + str(res)
            log_action("Full IP Scan", res)
        elif selection == "2":
            ip = input("Enter IP: ")
            res = scan_ports_range(f"{ip}-{ip}", [22, 3333, 4444, 5555])
            state.left_content = f"Quick scan for {ip}:\n" + str(res)
            log_action("Quick Port Scan", res)
        elif selection == "3":
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT action, result, time FROM logs ORDER BY id DESC LIMIT 10")
            logs = c.fetchall()
            state.right_content = "\n".join([f"{a}: {r} [{t}]" for a, r, t in logs])
            conn.close()
        elif selection == "4":
            cmd = input("Enter shell command: ")
            output = custom_command(cmd)
            state.right_content = f"Custom Command Output:\n{output}"
            log_action("Custom Command", output)
        elif selection == "5":
            txt = input("Text for AI: ")
            pred = ai_predict(txt)
            state.right_content = pred
            log_action("AI Prediction", pred)
        elif selection == "6":
            res = custom_command("netstat -an")
            state.right_content = "Netstat:\n" + res
            log_action("Netstat", res)
        elif selection == "7":
            event.app.exit()
        else:
            state.left_content = "Invalid selection."
        refresh()

    @kb.add("f5")
    def _(event):
        ip_range = input("Enter IP range for scan (start-end): ")
        ports = [22, 3333, 4444, 5555, 7777, 8888]
        res = scan_ports_range(ip_range, ports)
        state.left_content = "Scan Results:\n" + str(res)
        log_action("Scan", res)
        refresh()

    @kb.add("f6")
    def _(event):
        txt = input("Text for AI: ")
        pred = ai_predict(txt)
        state.right_content = pred
        log_action("AI Prediction", pred)
        refresh()

    @kb.add("f7")
    def _(event):
        output = custom_command("ls -al" if os.name != "nt" else "dir")
        state.right_content = "Files:\n" + output
        refresh()

    @kb.add("f8")
    def _(event):
        script = input("Enter Python code (one line): ")
        try:
            exec(script, globals())
            log_action("Script", script)
            state.right_content = "Script executed."
        except Exception as e:
            state.right_content = f"Script error: {e}"
        refresh()

    @kb.add("f9")
    def _(event):
        act = input("Enter custom action (type 'whoami' or any shell): ")
        output = custom_command(act)
        state.right_content = f"Custom Action Output:\n{output}"
        log_action("Custom Action", output)
        refresh()

    # === LAYOUT ===
    root_container = HSplit([
        Window(FormattedTextControl(HEADER), height=1, style="class:menu-bar"),
        VSplit([
            Frame(left_panel, title="Left Panel", style="class:frame.label"),
            Window(width=2, char=" ", style="bg:#0000aa"),
            Frame(right_panel, title="Right Panel", style="class:frame.label"),
        ]),
        Window(FormattedTextControl(FOOTER), height=1, style="class:footer"),
    ])

    layout = Layout(root_container, focused_element=left_panel)

    app = Application(
        layout=layout,
        key_bindings=kb,
        style=NC_STYLE,
        full_screen=True,
        mouse_support=True,
    )
    app.run()

if __name__ == "__main__":
    main()