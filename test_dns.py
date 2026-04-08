from dnslib import DNSRecord, RR, A, QTYPE
from socketserver import UDPServer, BaseRequestHandler
import time

class TestHandler(BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        addr = self.client_address
        print(f"📥 Получен запрос от {addr}")
        
        try:
            request = DNSRecord.parse(data)
            print(f"   Запрос: {request.q.qname} type={QTYPE.get(request.q.qtype)}")
            
            reply = request.reply()
            reply.header.aa = True
            
            # Возвращаем тестовый IP
            reply.add_answer(RR(rname=request.q.qname, rtype=QTYPE.A, ttl=60, rdata=A("1.2.3.4")))
            
            socket.sendto(reply.pack(), addr)
            print("   ✅ Ответ отправлен (1.2.3.4)")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

print("Запуск тестового DNS сервера на порту 10000...")
server = UDPServer(("0.0.0.0", 10000), TestHandler)
print("Сервер запущен. Тестируй сейчас...")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Остановлен")