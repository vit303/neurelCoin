import asyncio
import random
from datetime import datetime

from .peer_store import PeerStore
from .protocol import connect_and_get_peers
from .config import config


class Crawler:
    def __init__(self, store: PeerStore):
        self.store = store
        self.running = False

    async def start(self):
        self.running = True
        print("Crawler started")

        # Первоначальный bootstrap
        await self.bootstrap()

        while self.running:
            await self.crawl()
            await asyncio.sleep(config.crawl_interval)

    async def bootstrap(self):
        for peer in config.bootstrap_peers:
            try:
                nodes = await connect_and_get_peers(peer)
                for node in nodes:
                    self.store.add_node(node)
            except:
                continue

    async def crawl(self):
        print(f"Crawling network... Current nodes: {len(self.store.nodes)}")
        # Берём случайные 50 активных пиров
        active = list(self.store.nodes.values())
        if not active:
            await self.bootstrap()
            return

        sample = random.sample(active, min(50, len(active)))

        tasks = [connect_and_get_peers(f"{node.addresses[0].ip}:{node.addresses[0].port}") 
                for node in sample if node.addresses]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                for node in result:
                    self.store.add_node(node)