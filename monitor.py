#!/usr/bin/env python3
"""监控批处理进度"""

import time
import subprocess
import re

LOG_FILE = "/tmp/batch_process_new.log"

def get_progress():
    try:
        with open(LOG_FILE, 'r') as f:
            content = f.read()

        total_match = re.search(r'数据库中共有 (\d+) 条', content)
        current_match = re.findall(r'\[(\d+)/(\d+)\]', content)

        if current_match:
            last_current = int(current_match[-1][0])
            last_total = int(current_match[-1][1])

            total = int(total_match.group(1))
            percent = (last_current / last_total) * 100

            return last_current, last_total, percent
        return None, None, None
    except Exception as e:
        print(f"读取日志失败: {e}")
        return None, None, None

def main():
    print(f"📊 监控批处理进度...")
    print(f"日志文件: {LOG_FILE}\n")

    try:
        while True:
            current, total, percent = get_progress()

            if current is None:
                print("⏳ 等待处理开始...")
            else:
                print(f"进度: {current}/{total} ({percent:.1f}%)")

            time.sleep(10)
    except KeyboardInterrupt:
        print("\n\n监控已停止")
        current, total, percent = get_progress()
        if current is not None:
            print(f"\n最终进度: {current}/{total} ({percent:.1f}%)")

if __name__ == "__main__":
    main()
