import asyncio
from collections import deque
from better_proxy import Proxy
from core.utils.file_manager import file_to_list
import random
from queue import Queue

class ProxyPool:
    def __init__(self, proxy_file):
        self.proxy_queue = Queue()
        self.load_proxies_from_file(proxy_file)

    def load_proxies_from_file(self, proxy_file):
        try:
            with open(proxy_file, 'r') as file:
                for line in file:
                    proxy = line.strip()
                    if proxy:
                        self.proxy_queue.put(proxy)
        except FileNotFoundError:
            print(f"Ошибка: Файл {proxy_file} не найден!")

    def get_proxy(self):
        if self.proxy_queue.empty():
            print("Все прокси использованы. Перезагружаем пул.")
            return None
        return self.proxy_queue.get()

    def return_proxy(self, proxy):
        self.proxy_queue.put(proxy)

    def size(self):
        return self.proxy_queue.qsize()

proxies = deque()

lock = asyncio.Lock()


def load_proxy(proxy_path):
    global proxies
    proxies = deque([Proxy.from_str(proxy).as_url for proxy in file_to_list(proxy_path)])


async def get_proxy():
    """Return the first available proxy."""
    global proxies

    async with lock:
        if proxies:
            proxy = proxies.popleft()
            return proxy
        return None


async def release_proxy(proxy: str):
    """Release the proxy back into the available pool."""
    global proxies

    async with lock:
        proxies.append(proxy)
