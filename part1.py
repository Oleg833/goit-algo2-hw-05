import hashlib
import math
import bitarray

class BloomFilter:
    def __init__(self, size, num_hashes):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bitarray.bitarray(size)
        self.bit_array.setall(0)

    def _hashes(self, item):
        """Generate multiple hash values for the item."""
        hash_results = []
        for i in range(self.num_hashes):
            hash_value = int(hashlib.md5((item + str(i)).encode()).hexdigest(), 16) % self.size
            hash_results.append(hash_value)
        return hash_results

    def add(self, item):
        """Add an item to the Bloom Filter."""
        for hash_value in self._hashes(item):
            self.bit_array[hash_value] = 1

    def contains(self, item):
        """Check if an item is in the Bloom Filter."""
        return all(self.bit_array[hash_value] for hash_value in self._hashes(item))

def check_password_uniqueness(bloom_filter, passwords):
    """Check uniqueness of passwords using the Bloom Filter."""
    results = {}
    for password in passwords:
        if not password or not isinstance(password, str):
            results[password] = "некоректний пароль"
            continue

        if bloom_filter.contains(password):
            results[password] = "вже використаний"
        else:
            results[password] = "унікальний"
            bloom_filter.add(password)
    return results

if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' - {status}.")
