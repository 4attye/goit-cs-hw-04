from multiprocessing import Process, Manager
import os
from pathlib import Path
import threading
import time


thread_results = []
lock = threading.Lock()


# Розділяємо список файлів на частини для обробки потоками
def file_list_splitting(file_list, num_parts):
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


def print_results(results, mode, keyword, duration):
    print(f"\nРезультат для {mode}:")
    print(f"Час виконання: {duration:.5f} секунд")
    if not results:
        print(f"Не знайдено файлів з ключовим словом '{keyword}' у {mode}.")
    else:
        for result in results:
            print({keyword: result})


def main(data_dir):
        while True:

            # Отримуємо ключове слово від користувача
            keyword = input("Введіть ключове слово для пошуку, або 'exit' для виходу: ")

            if keyword.strip():
                if keyword.lower() == "exit":
                    break

                while True:
                    try:
                        # Отримуємо кількість потоків/процесів від користувача
                        num_threads_processes = int(input("Введіть кількість потоків(процесів): "))
                        break

                    except ValueError:
                        print("Будь ласка, введіть число.")
                        continue

                # Перевіряємо, чи існує директорія з даними
                if not os.path.isdir(data_dir):
                    print(f"Директорія '{data_dir}' не існує.")
                    break

                # Отримуємо список текстових файлів у директорії
                file_list = [str(Path(data_dir) / f) for f in os.listdir(data_dir) if f.endswith('.txt')]

                # Якщо немає текстових файлів, виводимо повідомлення і завершуємо цикл
                if not file_list:
                    print(f"У директорії '{data_dir}' не знайдено текстових файлів.")
                    break

                # Розділяємо список файлів на частини для потоків/процесів
                file_parts = file_list_splitting(file_list, num_threads_processes)

                # Очищення результатів перед кожним запуском
                thread_results.clear()
                start_time = time.time()

                # Створення та запуск потоків
                threads = []
                for i in range(num_threads_processes):
                    thread = threading.Thread(target=thread_worker, args=(file_parts[i], keyword))
                    threads.append(thread)
                    thread.start()

                # Чекаємо завершення всіх потоків
                for thread in threads:
                    thread.join()

                end_time = time.time()

                # Виводимо результати для потоків
                print_results(thread_results, "threading", keyword, end_time - start_time)

                # Очищення результатів перед запуском процесів
                multiprocessing_results = Manager().list()
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

                # Виводимо результати для процесів
                print_results(multiprocessing_results, "multiprocessing", keyword, end_time - start_time)


if __name__ == "__main__":

    data_dir = ("data") # Директорія з текстовими файлами
    main(data_dir) # Запуск основної функції

    # Ключові слова для тестування:
    # python, threading, multiprocessing, file, global, lock, processing, error, logging.