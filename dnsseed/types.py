from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum


class AddressType(IntEnum):
    IPv4 = 1
    IPv6 = 2
    TorV2 = 4
    TorV3 = 8
    I2P = 16
    CJDNS = 32


@dataclass
class NodeAddress:
    ip: str
    port: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    type: AddressType = AddressType.IPv4


@dataclass
class Node:
    node_id: bytes
    addresses: list[NodeAddress] = field(default_factory=list)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    last_check: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    version: int = 70016
    services: int = 0
    user_agent: str = ""


@dataclass
class QueryConditions:
    realm: int = 0
    address_type: int = 3          # IPv4 + IPv6
    node_id: bytes | None = None
    num_results: int = 25
    is_node_query: bool = False