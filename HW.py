from multiprocessing import Process, Manager
import os
from pathlib import Path
import threading
import time


thread_results = []
lock = threading.Lock()


# Розділяємо список файлів на частини для обробки потоками
def split_list_files(file_list, num_parts):
    k, m = divmod(len(file_list), num_parts)
    return [file_list[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(num_parts)]


# Функція для обробки файлів у потоках
def thread_worker(file_list, keyword):
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if keyword.lower() in content.lower():
                    with lock:
                        thread_results.append(file_path)
        except Exception as e:
            print(f"Помилка при обробці файлу {file_path}: {e}")


# Функція для обробки файлів у процесах
def multiprocessing_worker(file_list, keyword, result_list):
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if keyword.lower() in content.lower():
                    result_list.append(file_path)
        except Exception as e:
            print(f"Помилка при обробці файлу {file_path}: {e}")


def main(data_dir):
        while True:

            # Отримання ключового слова від користувача
            keyword = input("Введіть ключове слово для пошуку, або 'exit' для виходу: ")

            if keyword.strip():
                if keyword.lower() == "exit":
                    break

                while True:
                    try:
                        # Отримання кількості потоків/процесів від користувача
                        num_threads_processes = int(input("Введіть кількість потоків(процесів): "))
                        break

                    except ValueError:
                        print("Будь ласка, введіть число.")
                        continue

                # Перевірка наявності директорії
                if not os.path.isdir(data_dir):
                    print(f"Директорія '{data_dir}' не існує.")
                    break

                file_list = [str(Path(data_dir) / f) for f in os.listdir(data_dir) if f.endswith('.txt')]

                if not file_list:
                    print(f"У директорії '{data_dir}' не знайдено текстових файлів.")
                    break

                # Розділіть список файлів на частини для обробки потоками
                file_parts = split_list_files(file_list, num_threads_processes)

                # Очищення результатів перед кожним запуском
                thread_results.clear()
                start_time = time.time()

                # Створіть та запустіть потоки
                threads = []
                for i in range(num_threads_processes):
                    thread = threading.Thread(target=thread_worker, args=(file_parts[i], keyword))
                    threads.append(thread)
                    thread.start()

                # Чекаємо завершення всіх потоків
                for thread in threads:
                    thread.join()

                end_time = time.time()
                print(f"\nРезультат для потоків:")
                print(f"Час виконання: {end_time - start_time:.5f} секунд")
                if not thread_results:
                    print(f"Не знайдено файлів з ключовим словом '{keyword}' у потоках.")
                else:
                    for result in thread_results:
                        print({keyword: result})

                # Запускаємо таймер для процесів
                multiprocessing_results = manager.list()  # Використовуємо менеджер для спільного списку
                start_time = time.time()

                # Перевірка кількості процесів, якщо їх більше ніж файлів вставлюємо кількість процесів рівну кількості файлів
                num_threads_processes = min(num_threads_processes, len(file_list))

                # Створення та запуск процесів
                processes = []
                for i in range(num_threads_processes):
                    process = Process(
                        target=multiprocessing_worker,
                        args=(file_parts[i], keyword, multiprocessing_results)
                    )
                    processes.append(process)
                    process.start()

                # Чекаємо завершення всіх процесів
                for process in processes:
                    process.join()

                end_time = time.time()
                print(f"\nРезультат для процесів:")
                print(f"Час виконання: {end_time - start_time:.5f} секунд")
                if not multiprocessing_results:
                    print(f"Не знайдено файлів з ключовим словом '{keyword}' у процесах.")
                else:
                    for result in multiprocessing_results:
                        print({keyword: result})


if __name__ == "__main__":
    
    manager = Manager()
    data_dir = ("data") # Директорія з текстовими файлами
    main(data_dir)