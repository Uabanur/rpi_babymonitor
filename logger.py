import sys

def debug(msg: str):
    write("DEBUG: " + msg)

def info(msg: str):
    write("INFO: " + msg)

def error(msg: str):
    write("ERROR: " + msg)

def write(msg: str):
    print(msg)
    # flush stdout to show prints in journalctl logs
    sys.stdout.flush()
