import asyncio
import threading
import time
from socketserver import UDPServer, BaseRequestHandler

from dnsseed.dns_handler import DNSSeedHandler
from dnsseed.peer_store import PeerStore
from dnsseed.crawler import Crawler
from dnsseed.config import config


store = None


class DNSRequestHandler(BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        try:
            response = self.server.dns_handler.handle(data, self.client_address)
            socket.sendto(response, self.client_address)
        except Exception as e:
            print(f"Handler error: {e}")


def run_dns_server():
    global store
    try:
        server = UDPServer((config.listen_host, config.listen_port), DNSRequestHandler)
        server.dns_handler = DNSSeedHandler(store, config.domain, config.ttl)
        
        print(f"🌐 DNS Seed успешно запущен на {config.listen_host}:{config.listen_port}")
        print(f"   Тест: python test_client.py")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def main():
    global store
    store = PeerStore()
    print("Crawler started")

    dns_thread = threading.Thread(target=run_dns_server, daemon=True)
    dns_thread.start()

    time.sleep(1.5)  # даём серверу запуститься

    crawler = Crawler(store)
    await crawler.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 DNS Seed остановлен")