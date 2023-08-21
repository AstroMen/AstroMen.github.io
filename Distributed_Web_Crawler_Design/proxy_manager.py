import threading
import time
import requests
from collections import deque, defaultdict


class ProxyManager:
    def __init__(self, initial_proxies):
        self.lock = threading.Lock()  # To avoid race conditions when updating proxies
        self.proxies = deque(initial_proxies)  # Use deque for rotation
        self.proxy_scores = defaultdict(int)  # Higher is better
        self.proxy_fail_count = defaultdict(int)

    def validate_proxy(self, proxy):
        test_url = "https://www.google.com"  # A common choice, but you might want to use another URL
        try:
            response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=5)
            return response.status_code == 200
        except:
            return False

    def validate_all_proxies(self):
        with self.lock:
            valid_proxies = [proxy for proxy in self.proxies if self.validate_proxy(proxy)]
            self.proxies = deque(valid_proxies)

    def get_proxy(self):
        with self.lock:
            if not self.proxies:
                return None
            # Rotate the proxy to the end
            proxy = self.proxies.popleft()
            self.proxies.append(proxy)
            return proxy

    def run_periodic_validation(self, interval=300):  # Default is 5 minutes
        while True:
            self.validate_all_proxies()
            time.sleep(interval)

    def report_proxy_success(self, proxy):
        with self.lock:
            self.proxy_scores[proxy] += 1
            self.proxy_fail_count[proxy] = 0

    def report_proxy_failure(self, proxy):
        with self.lock:
            self.proxy_scores[proxy] -= 1
            self.proxy_fail_count[proxy] += 1
            # Remove proxy if it fails too often consecutively
            if self.proxy_fail_count[proxy] > 5:  # Threshold can be adjusted
                self.proxies.remove(proxy)