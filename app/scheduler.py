import datetime
import os
import subprocess
import time
import json
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

BIN_PATH = Path("/app/twitter_download")
CONFIG_PATH = Path("/config")
SAVE_PATH = Path("/download")

DEFAULT_INTERVAL = 60 * 60 * 24
DEFAULT_RETRY_TIMES = 1

def task(total_attempts: int = DEFAULT_RETRY_TIMES, delete_csv: bool = False):
    config_file = CONFIG_PATH / "settings.json"
    dest_file = BIN_PATH / "settings.json"

    try:
        data = json.loads(config_file.read_text(encoding="utf-8"))
        data["save_path"] = str(SAVE_PATH)
        dest_file.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"failed to update config: {e}")
        return
    
    print(f"wrote updated config to {dest_file}")
    
    for attempt in range(total_attempts):
        try:
            subprocess.run(["python3", "-u", "main.py"], cwd=BIN_PATH, check=True, timeout=60 * 60 * 24)
            print(f"twitter_download attempt {attempt + 1} succeeded")
            break
        except Exception as e:
            print(f"twitter_download attempt {attempt + 1} / {total_attempts} failed: {e}")
            if attempt + 1 == total_attempts:
                print(f"all {total_attempts} attempts failed")
                return
            else:               
                time.sleep(10)

    print("twitter_download succeeded")
    
    if delete_csv:
        print("deleting csv...")
        for file in SAVE_PATH.rglob("*"):
            if file.is_file() and file.suffix.casefold() == ".csv":
                try:
                    file.unlink()
                    print(f"deleted: {file}")
                except OSError as e:
                    print(f"failed to delete {file}: {e}")

if __name__ == "__main__":    
    try:
        interval = int(os.environ.get("INTERVAL", ""))
        if interval <= 60:
            raise ValueError(f"interval should longer than 60 seconds, using default {DEFAULT_INTERVAL}")
    except ValueError:
        interval = DEFAULT_INTERVAL
        
    try:
        retry_times = int(os.getenv("RETRY_TIMES", ""))
        if not (0 <= retry_times <= 10):
            raise ValueError(f"retry_times should in [0-10], using default {DEFAULT_RETRY_TIMES}")
    except ValueError:
        retry_times = DEFAULT_RETRY_TIMES
        
    delete_csv = os.environ.get("DELETE_CSV", "").strip().lower() == "true"
    
    print(f"==========\nretry_times = {retry_times}\ninterval = {interval}\ndelete_csv = {delete_csv}\n==========\n")

    scheduler.add_job(task, 'interval', seconds=interval, next_run_time=datetime.datetime.now(), args=[retry_times + 1, delete_csv])
    scheduler.start()
