from dataclasses import dataclass, field
from typing import List

@dataclass
class Config:
    domain: str = "mainnet.seeder.example.com"
    ttl: int = 600
    listen_host: str = "0.0.0.0"
    listen_port: int = 10000          # ← Изменено на 10000
    crawl_interval: int = 1800
    max_nodes: int = 50000
    
    bootstrap_peers: List[str] = field(default_factory=lambda: [
        "seed.bitcoin.sipa.be:8333",
        "dnsseed.bluematt.me:8333",
        "seed.bitcoinstats.com:8333",
    ])

config = Config()