import datetime
import os
import subprocess
import sys
import shutil
import time
import json

from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

bin_path = "/app/twitter_download"
config_path = "/config"
save_path = "/download"

DEFAULT_INTERVAL = 60 * 60 * 24
DEFAULT_RETRY_TIMES = 1

retry_times = None
interval = None
delete_csv = False

def update_all():
    config_file = os.path.join(config_path, "settings.json")
    dest_file =  os.path.join(bin_path, "settings.json")

    if os.path.exists(config_file):
        shutil.copy(config_file, dest_file)
        print(f"Copied {config_file} to {dest_file}")
        try:
            with open(dest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading JSON from {dest_file}: {e}")
            return -1
        data["save_path"] = save_path
        
        try:
            with open(dest_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error writing JSON to {dest_file}: {e}")
            return -1

        print(f"Updated 'save_path' in {dest_file} to '{save_path}'")
    else:
        print(f"Config file {config_file} not found")
        return -1

    process = subprocess.Popen(
        ["python3", "./main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=bin_path
    )
    out, _ = process.communicate()
    print(out.decode(), end="")
    
    return_code = process.returncode
    
    print(f"return {return_code}")
    
    if return_code == 0 and delete_csv:
        print("start deleting csv")
        for dirpath, dirnames, filenames in os.walk(save_path):
            for name in filenames:
                if name.lower().endswith(".csv"):
                    full_path = os.path.join(dirpath, name)
                    try:
                        os.remove(full_path)
                        print(f"deleted: {full_path}")
                    except Exception as e:
                        print(f"failed to delete {full_path}: {e}")

    return return_code

def task():
    for attempt in range(retry_times + 1):
        try:
            rc = update_all()
        except Exception as e:
            rc = -1
            print("update_all failed:", e)
        if rc == 0:
            break
        if attempt < retry_times:
            time.sleep(10)

if __name__ == "__main__":    
    raw = os.environ.get("INTERVAL", "")
    try:
        interval = int(raw)
        if interval <= 60:
            raise ValueError("interval should longer than 60 seconds")
    except (ValueError, TypeError):
        interval = DEFAULT_INTERVAL
        
    raw = os.getenv("RETRY_TIMES", "")

    try:
        retry_times = int(raw)
        if not (0 <= retry_times <= 10):
            raise ValueError("retry_times should in [0-10]")
    except (ValueError, TypeError):
        retry_times = DEFAULT_RETRY_TIMES
        
    if os.environ.get("DELETE_CSV", "").strip().lower() == "true":
        delete_csv = True
    
    print(f"retry_times={retry_times}\ninterval={interval}\ndelete_csv={delete_csv}\n")

    scheduler.add_job(task, 'interval', seconds=interval, next_run_time=datetime.datetime.now())
    scheduler.start()
