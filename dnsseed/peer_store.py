import random
import time
from datetime import datetime, timedelta
from typing import Dict, List

from dnsseed.types import Node, NodeAddress, AddressType


class PeerStore:
    def __init__(self):
        self.nodes: Dict[bytes, Node] = {}
        self._active_cache: List[Node] = []
        self._cache_time = 0.0
        self._cache_ttl = 300

        # === Добавляем тестовые ноды для проверки ===
        self._add_test_nodes()

    def _add_test_nodes(self):
        """Добавляем несколько тестовых узлов"""
        test_nodes = [
            ("192.168.1.10", 8333, AddressType.IPv4),
            ("192.168.1.11", 8333, AddressType.IPv4),
            ("192.168.1.12", 8333, AddressType.IPv4),
            ("2001:db8::1", 8333, AddressType.IPv6),
            ("2001:db8::2", 8333, AddressType.IPv6),
            ("1.2.3.4", 8333, AddressType.IPv4),
            ("5.6.7.8", 8333, AddressType.IPv4),
        ]

        for i, (ip, port, addr_type) in enumerate(test_nodes):
            node_id = f"testnode{i:03d}".encode().ljust(32, b'\0')
            node = Node(
                node_id=node_id,
                addresses=[NodeAddress(ip=ip, port=port, type=addr_type)],
                last_seen=datetime.utcnow(),
                is_active=True,
                version=70016,
                user_agent=f"/Satoshi:25.0.0/"
            )
            self.add_node(node)

        print(f"✅ Добавлено {len(test_nodes)} тестовых нод для тестирования")

    def add_node(self, node: Node):
        if node.node_id in self.nodes:
            existing = self.nodes[node.node_id]
            existing.last_seen = node.last_seen
            existing.is_active = node.is_active
            addr_map = {a.ip: a for a in existing.addresses}
            for new_addr in node.addresses:
                addr_map[new_addr.ip] = new_addr
            existing.addresses = list(addr_map.values())
        else:
            self.nodes[node.node_id] = node

        self._cache_time = 0  # invalidate cache

    def get_random_active_nodes(self, count: int = 25, addr_type_mask: int = 3) -> List[Node]:
        if time.time() - self._cache_time > self._cache_ttl:
            self._refresh_cache()

        filtered = [
            node for node in self._active_cache
            if any((1 << int(a.type)) & addr_type_mask for a in node.addresses)
        ]

        random.shuffle(filtered)
        return filtered[:count]

    def get_node_by_id(self, node_id: bytes) -> Node | None:
        return self.nodes.get(node_id)

    def _refresh_cache(self):
        now = datetime.utcnow()
        self._active_cache = [
            node for node in self.nodes.values()
            if node.is_active and (now - node.last_seen) < timedelta(hours=24)
        ]
        self._cache_time = time.time()