import logging
from kazoo.client import KazooClient
from kazoo.client import KazooState

logging.basicConfig(level=logging.INFO)


class ZookeeperService:
    def __init__(self, hosts):
        self.zk = KazooClient(hosts=hosts)
        self.zk.start()
        self.zk.add_listener(self._state_listener)

    def _state_listener(self, state):
        if state == KazooState.LOST:
            logging.error("Zookeeper connection lost!")
        elif state == KazooState.SUSPENDED:
            logging.warning("Zookeeper connection suspended!")
        else:
            logging.info("Zookeeper connected!")

    def register_service(self, service_name, service_data):
        path = f"/services/{service_name}"
        return self.zk.create(path, value=service_data.encode(), ephemeral=True, sequence=True)

    def discover_service(self, service_name):
        path = f"/services/{service_name}"
        children = self.zk.get_children(path)
        # You can decide how you want to select a service instance here.
        # For simplicity, we're just getting the data of the first available child.
        if children:
            service_data, _ = self.zk.get(f"{path}/{children[0]}")
            return service_data.decode()
        return None

    def remove_service(self, full_path):
        if self.zk.exists(full_path):
            self.zk.delete(full_path)
        # Optionally, stop the ZooKeeper client after removing the service
        # self.stop()

    def stop(self):
        self.zk.stop()

    def update_service(self, full_path, new_data):
        if self.zk.exists(full_path):
            self.zk.set(full_path, new_data.encode())


import time
import threading

class ServiceManager:
    def __init__(self, zookeeper_service):
        self.zookeeper_service = zookeeper_service
        self.is_service_online = False
        self.check_interval = 60  # 1 minute

    def periodic_check(self):
        while True:
            self.is_service_online = self.zookeeper_service.discover_service('your_service_name')
            time.sleep(self.check_interval)

    def start_periodic_check(self):
        # Using threading to periodically check service availability
        threading.Thread(target=self.periodic_check, daemon=True).start()

    def handle_error(self, error):
        if isinstance(error, ConnectionError):  # Replace with the appropriate exception for your case
            self.is_service_online = self.zookeeper_service.discover_service('your_service_name')
