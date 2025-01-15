import time
import json
from hashlib import sha256


# Function to count unique IPs safely with execution time tracking
def count_unique_ips_json_safe_with_time(file_path):
    unique_ips = set()
    invalid_lines = 0  # Counter for invalid lines
    start_time = time.time()  # Start timing
    try:
        with open(file_path, "r") as file:
            for line in file:
                try:
                    record = json.loads(line)
                    ip = record.get("remote_addr", "")
                    if ip:
                        unique_ips.add(ip)
                except json.JSONDecodeError:
                    invalid_lines += 1
        execution_time = time.time() - start_time  # Calculate execution time
        print(f"Некоректних рядків: {invalid_lines}")
        return len(unique_ips), execution_time
    except FileNotFoundError:
        print("Файл не знайдено.")
        return 0, 0
    except Exception as e:
        print(f"Помилка при обробці файлу: {e}")
        return 0, 0


# Function to count unique IPs using HyperLogLog
def count_unique_ips_hyperloglog(file_path, num_buckets=1024):
    buckets = [0] * num_buckets
    start_time = time.time()
    try:
        with open(file_path, "r") as file:
            for line in file:
                try:
                    record = json.loads(line)
                    ip = record.get("remote_addr", "")
                    if ip:
                        hash_value = int(sha256(ip.encode()).hexdigest(), 16)
                        bucket_index = hash_value % num_buckets
                        leading_zeros = len(
                            bin(hash_value // num_buckets).lstrip("0b").lstrip("0")
                        )
                        buckets[bucket_index] = max(
                            buckets[bucket_index], leading_zeros
                        )
                except json.JSONDecodeError:
                    continue
        alpha = 0.7213 / (1 + 1.079 / num_buckets)
        harmonic_mean = sum(2**-bucket for bucket in buckets)
        estimate = alpha * (num_buckets**2) / harmonic_mean
        execution_time = time.time() - start_time
        return round(estimate), execution_time
    except FileNotFoundError:
        print("Файл не знайдено.")
        return 0, 0
    except Exception as e:
        print(f"Помилка при обробці файлу: {e}")
        return 0, 0


# Function to compare exact and approximate methods
def compare_methods(file_path):
    exact_count, exact_time = count_unique_ips_json_safe_with_time(file_path)
    hll_count, hll_time = count_unique_ips_hyperloglog(file_path)

    print("Результати порівняння:")
    print(f"{'Метод':<20} | {'Унікальні елементи':<20} | {'Час виконання (сек.)':<20}")
    print(f"{'Точний підрахунок':<20} | {exact_count:<20} | {exact_time:<20.2f}")
    print(f"{'HyperLogLog':<20} | {hll_count:<20} | {hll_time:<20.2f}")


# Specify the log file path
log_file_path = "lms-stage-access.log"

# Execute comparison
compare_methods(log_file_path)
