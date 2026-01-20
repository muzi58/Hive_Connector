#!/usr/bin/env python3
"""
Hive Connect 内存监控脚本
在后台监控应用的内存和 CPU 使用情况
"""

import psutil
import time
import sys
from datetime import datetime

def find_hive_connect_process():
    """查找 Hive Connect 进程"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 查找包含 "Hive Connect" 或 main.py 的进程
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'Hive Connect' in cmdline or 'main.py' in cmdline:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def format_bytes(bytes_value):
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"

def monitor_process(interval=2):
    """监控进程"""
    print("正在查找 Hive Connect 进程...")
    proc = find_hive_connect_process()
    
    if not proc:
        print("❌ 未找到 Hive Connect 进程")
        print("请先启动应用！")
        return
    
    print(f"✅ 找到进程 PID: {proc.pid}")
    print(f"\n开始监控（每 {interval} 秒更新一次，按 Ctrl+C 停止）")
    print("=" * 80)
    print(f"{'时间':<20} {'内存(RSS)':<15} {'CPU %':<10} {'线程数':<10}")
    print("=" * 80)
    
    max_memory = 0
    max_cpu = 0
    
    try:
        while True:
            try:
                # 获取内存信息
                mem_info = proc.memory_info()
                rss = mem_info.rss  # 常驻内存
                
                # 获取 CPU 使用率
                cpu_percent = proc.cpu_percent(interval=0.1)
                
                # 获取线程数
                num_threads = proc.num_threads()
                
                # 更新峰值
                max_memory = max(max_memory, rss)
                max_cpu = max(max_cpu, cpu_percent)
                
                # 输出
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{timestamp:<20} {format_bytes(rss):<15} {cpu_percent:<10.1f} {num_threads:<10}")
                
                time.sleep(interval)
                
            except psutil.NoSuchProcess:
                print("\n⚠️  进程已结束")
                break
                
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("监控已停止")
        print(f"\n📊 统计信息:")
        print(f"  峰值内存: {format_bytes(max_memory)}")
        print(f"  峰值 CPU: {max_cpu:.1f}%")
        print("=" * 80)

if __name__ == "__main__":
    monitor_process()
