import subprocess

selected_range = "192.168.1.0/24"  # از انتخاب کاربر بگیر
ports = "3333,4444,5555,7777,8888,18081,18082,18083,4028,4233,8233"

cmd = [
    "nmap", "-sS", "-p", ports, "--open", "-T4", "-oN", "scan.log", selected_range
]

with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
    for line in proc.stdout:
        print(line, end="")  # خروجی زنده به کاربر نمایش داده شود