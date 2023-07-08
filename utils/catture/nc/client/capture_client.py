import subprocess, time, os, datetime

RECV_PORT = "9999"

cmd = f"nc -w1 -nvlp {RECV_PORT} > catture.zip"
os.system(cmd)
