from dnslib import DNSRecord, QTYPE
import socket

def dns_query(name: str, qtype="A", port=10000):
    print(f"\n🔍 Запрос: {name} ({qtype})")
    q = DNSRecord.question(name, qtype)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    
    s.sendto(q.pack(), ("127.0.0.1", port))
    data, _ = s.recvfrom(2048)
    
    reply = DNSRecord.parse(data)
    print(reply)
    
    s.close()

# Тесты
if __name__ == "__main__":
    dns_query("mainnet.seeder.example.com")
    dns_query("a2.n10.mainnet.seeder.example.com")
    dns_query("a1.n5.mainnet.seeder.example.com")
    dns_query("a3.n15.mainnet.seeder.example.com")   # IPv4 + IPv6