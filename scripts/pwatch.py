import os
import time
import psutil

"""Small script that wait for a process to finish to issue a computer shutdown."""

p_watch = 8320

while True:
    pids = [proc.pid for proc in psutil.process_iter(attrs=None, ad_value=None)]
    if p_watch not in pids:
        os.system("shutdown /s /t 5");
        break
    time.sleep(60*10)
