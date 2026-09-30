import time

import requests


def sync_requests():
    url = 'http://127.0.0.1:8000/sync'
    print('=' * 30)
    print('Синхронные запросы')

    start = time.time()

    for i in range(50):
        response = requests.get(f"{url}/{i}")
        if i % 10 == 0:
            print(f'Прогресс {i+1}/100')

    end = time.time()

    print(f'Синхронные запросы выполнились за {end - start:.2f}')
    print('=' * 30)
