import time
import json
from mmh3 import hash as murmurhash
from xxhash import xxh64  # Використовуємо xxhash для кращого розподілу хешів


# Функція для підрахунку унікальних IP-адрес точно (з відстеженням часу виконання)
def count_unique_ips_json_safe_with_time(file_path):
    unique_ips = set()
    invalid_lines = 0  # Лічильник некоректних рядків
    start_time = time.time()  # Початок вимірювання часу
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
        execution_time = time.time() - start_time  # Час виконання
        print(f"Некоректних рядків: {invalid_lines}")
        return len(unique_ips), execution_time
    except FileNotFoundError:
        print("Файл не знайдено.")
        return 0, 0
    except Exception as e:
        print(f"Помилка при обробці файлу: {e}")
        return 0, 0


# Функція для підрахунку унікальних IP-адрес за допомогою HyperLogLog (Покращена версія)
def count_unique_ips_hyperloglog(
    file_path, num_buckets=32, runs=10
):  # Зменшено до 64 кошиків
    total_estimate = 0
    total_time = 0
    for _ in range(runs):
        buckets = [0] * num_buckets
        start_time = time.time()
        try:
            with open(file_path, "r") as file:
                for line in file:
                    try:
                        record = json.loads(line)
                        ip = record.get("remote_addr", "")
                        if ip:
                            # Використовуємо дві хеш-функції для зменшення колізій
                            hash_value1 = murmurhash(ip)  # Перша хеш-функція
                            hash_value2 = xxh64(
                                ip.encode("utf-8")
                            ).intdigest()  # Друга хеш-функція
                            hash_value = (
                                hash_value1 ^ hash_value2
                            )  # Комбінація двох хешів
                            bucket_index = hash_value % num_buckets
                            # Використовуємо bit_length для більш ефективного обчислення провідних нулів
                            leading_zeros = (
                                (hash_value.bit_length() - bucket_index.bit_length())
                                if hash_value > bucket_index
                                else 0
                            )
                            buckets[bucket_index] = max(
                                buckets[bucket_index], leading_zeros
                            )
                    except json.JSONDecodeError:
                        continue
            # Покращена корекція alpha для 64 кошиків
            alpha = 0.7213 / (1 + 1.079 / num_buckets)
            harmonic_mean = sum(2**-bucket for bucket in buckets)
            estimate = alpha * (num_buckets**2) / harmonic_mean
            execution_time = time.time() - start_time
            total_estimate += estimate
            total_time += execution_time
        except FileNotFoundError:
            print("Файл не знайдено.")
            return 0, 0
        except Exception as e:
            print(f"Помилка при обробці файлу: {e}")
            return 0, 0

    # Підрахунок середнього значення оцінки та часу виконання
    avg_estimate = total_estimate / runs
    avg_time = total_time / runs
    return round(avg_estimate), avg_time


# Функція для порівняння точного методу та HyperLogLog
def compare_methods(file_path):
    exact_count, exact_time = count_unique_ips_json_safe_with_time(file_path)
    hll_count, hll_time = count_unique_ips_hyperloglog(file_path)

    print("Результати порівняння:")
    print(f"{'Метод':<20} | {'Унікальні елементи':<20} | {'Час виконання (сек.)':<20}")
    print(f"{'Точний підрахунок':<20} | {exact_count:<20} | {exact_time:<20.2f}")
    print(f"{'HyperLogLog':<20} | {hll_count:<20} | {hll_time:<20.2f}")


log_file_path = "lms-stage-access.log"


compare_methods(log_file_path)
