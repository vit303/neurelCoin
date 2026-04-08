import asyncio
import struct
import hashlib
from datetime import datetime

from .types import Node, NodeAddress, AddressType


async def connect_and_get_peers(peer_addr: str, timeout=10) -> list[Node]:
    """Простая реализация получения addr через Bitcoin P2P"""
    try:
        host, port = peer_addr.split(':')
        reader, writer = await asyncio.open_connection(host, int(port), timeout=timeout)

        # version message (упрощённо)
        version_msg = b'\xf9\xbe\xb4\xd9' + b'version' + b'\x00'*5 + struct.pack('<I', 70016)
        writer.write(version_msg)
        await writer.drain()

        # Здесь в реальной реализации нужно полноценно обработать verack, getaddr и addr
        # Для примера возвращаем заглушку
        await asyncio.sleep(2)

        # Имитация получения адресов
        nodes = []
        for _ in range(5):
            nodes.append(Node(
                node_id=hashlib.sha256(f"fake{_:02d}".encode()).digest(),
                addresses=[NodeAddress(ip="192.168.1.1", port=8333, type=AddressType.IPv4)],
                last_seen=datetime.utcnow(),
                is_active=True
            ))

        writer.close()
        await writer.wait_closed()
        return nodes

    except Exception:
        return []