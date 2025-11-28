import time
import subprocess
import os
import json
import logging

import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Time helper
def ts():
    return time.strftime("%H:%M:%S")

# Paths
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_JAR = os.path.join(SERVER_DIR, "server.jar")
PLUGINS_DIR = os.path.join(SERVER_DIR, "plugins")
CONFIG_FILE = os.path.join(SERVER_DIR, "pwatchercfg.json")

# Default config
DEFAULT_CONFIG = {
    "ram_mode": "auto",
    "fixed_ram_gb": 4,
    "ram_fraction": 0.25,
    "max_ram_gb": None,
    "use_aikar_flags": True,
    "extra_java_args": [],
    "ignore_jars": []
}

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except:
            pass
    return cfg

CONFIG = load_config()

# RAM / JVM flags
total_ram_gb = int(psutil.virtual_memory().total / (1024**3))

if CONFIG["ram_mode"] == "fixed":
    alloc_gb = int(CONFIG["fixed_ram_gb"])
else:
    alloc_gb = max(1, int(total_ram_gb * float(CONFIG["ram_fraction"])))

if CONFIG["max_ram_gb"] is not None:
    alloc_gb = min(alloc_gb, int(CONFIG["max_ram_gb"]))

alloc_gb = max(alloc_gb, 1)

JAVA_FLAGS = [f"-Xms{alloc_gb}G", f"-Xmx{alloc_gb}G"]

if CONFIG["use_aikar_flags"]:
    JAVA_FLAGS.extend([
        "-XX:+UseG1GC",
        "-XX:+ParallelRefProcEnabled",
        "-XX:MaxGCPauseMillis=200",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+DisableExplicitGC",
        "-XX:+AlwaysPreTouch",
        "-XX:G1NewSizePercent=30",
        "-XX:G1MaxNewSizePercent=40",
        "-XX:G1HeapRegionSize=8M",
        "-XX:G1ReservePercent=20",
        "-XX:G1HeapWastePercent=5",
        "-XX:G1MixedGCCountTarget=4",
        "-XX:InitiatingHeapOccupancyPercent=15",
        "-XX:G1MixedGCLiveThresholdPercent=90",
        "-XX:G1RSetUpdatingPauseTimePercent=5",
        "-XX:SurvivorRatio=32",
        "-XX:+PerfDisableSharedMem",
        "-XX:MaxTenuringThreshold=1"
    ])

JAVA_FLAGS.extend(CONFIG["extra_java_args"])

# Server handling
server_process = None

def start_server():
    global server_process

    if server_process and server_process.poll() is None:
        return

    cmd = ["java"] + JAVA_FLAGS + ["-jar", SERVER_JAR, "nogui"]
    server_process = subprocess.Popen(cmd, cwd=SERVER_DIR)

def jar_is_ignored(jar_name: str):
    lower = jar_name.lower()
    for pat in CONFIG["ignore_jars"]:
        if pat.lower() in lower:
            return True
    return False

# Watchdog handler
class PluginWatcher(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return

        fname = os.path.basename(event.src_path).lower()

        if not fname.endswith(".jar"):
            return

        if jar_is_ignored(fname):
            return

        start_server()

# Main
if __name__ == "__main__":

    os.makedirs(PLUGINS_DIR, exist_ok=True)

    print(f"[{ts()}] [INFO] RAM detection: system={total_ram_gb} GB, allocating={alloc_gb} GB (mode={CONFIG['ram_mode']})")
    print(f"[{ts()}] [INFO] Config loaded.\n")
    print("Plugin Refresh Watcher Active...\n")

    observer = Observer()
    observer.schedule(PluginWatcher(), PLUGINS_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
