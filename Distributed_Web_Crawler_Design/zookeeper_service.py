from kazoo.client import KazooClient
from kazoo.client import KazooState


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

    def register_service(self, path, value):
        """Register a service with given path and value."""
        self.zk.ensure_path(path)
        self.zk.set(path, value.encode())

    def discover_service(self, path):
        """Discover service value by path."""
        if self.zk.exists(path):
            data, _ = self.zk.get(path)
            return data.decode()

    def remove_service(self, path):
        """Remove a registered service."""
        self.zk.delete(path, recursive=True)

    def close(self):
        self.zk.stop()
