import time
from collections import Counter

# Step 1: Load data from the log file
def load_log_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

# Step 2: Count unique IPs using a set
def count_unique_ips_set(file_path):
    unique_ips = set()
    start_time = time.time()
    for line in load_log_file(file_path):
        ip = line.split()[0]  # Assuming IP is the first element in each log line
        unique_ips.add(ip)
    execution_time = time.time() - start_time
    return len(unique_ips), execution_time

# Step 3: Count unique IPs using HyperLogLog
def count_unique_ips_hyperloglog(file_path):
    from datasketch import HyperLogLog
    hll = HyperLogLog()
    start_time = time.time()
    for line in load_log_file(file_path):
        ip = line.split()[0]  # Assuming IP is the first element in each log line
        hll.add(ip)
    execution_time = time.time() - start_time
    return len(hll), execution_time

# Step 4: Compare results
def compare_methods(file_path):
    exact_count, exact_time = count_unique_ips_set(file_path)
    hll_count, hll_time = count_unique_ips_hyperloglog(file_path)

    print("Результати порівняння:")
    print(f"\t{'':<15} Точний підрахунок | HyperLogLog")
    print(f"Унікальні елементи: {exact_count:<10} | {hll_count:<10}")
    print(f"Час виконання (сек.): {exact_time:<10.2f} | {hll_time:<10.2f}")

# Specify the log file path (replace with actual file path)
log_file_path = 'lms-stage-access.log'

# Execute comparison
compare_methods(log_file_path)
