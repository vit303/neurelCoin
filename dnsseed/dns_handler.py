from dnslib import DNSRecord, RR, A, AAAA, SRV, QTYPE
import ipaddress
import traceback

from dnsseed.types import QueryConditions, AddressType
from dnsseed.peer_store import PeerStore
from dnsseed.utils import parse_conditions


class DNSSeedHandler:
    def __init__(self, store: PeerStore, domain: str, ttl: int = 600):
        self.store = store
        self.domain = domain.lower().rstrip('.')
        self.ttl = ttl
        print(f"DNS Handler initialized for domain: {self.domain}")

    def handle(self, data: bytes, client_addr) -> bytes:
        print(f"📥 Received query from {client_addr}")
        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname).lower().rstrip('.')
            qtype = request.q.qtype
            print(f"   Query: {qname} (type={QTYPE.get(qtype)})")

            if not qname.endswith(self.domain):
                print("   Not our domain → NXDOMAIN")
                reply = request.reply()
                reply.header.rcode = 3
                return reply.pack()

            conditions = parse_conditions(qname)
            print(f"   Conditions: {conditions}")

            reply = request.reply()
            reply.header.aa = True

            if qtype == QTYPE.A:
                self._handle_a(reply, conditions)
            elif qtype == QTYPE.AAAA:
                self._handle_aaaa(reply, conditions)
            elif qtype == QTYPE.SRV:
                self._handle_srv(reply, conditions)
            else:
                reply.header.rcode = 4  # Not Implemented

            print(f"   Response: {len(reply.rr)} records")
            return reply.pack()

        except Exception as e:
            print("❌ ERROR in DNS handler:")
            print(traceback.format_exc())
            reply = DNSRecord.parse(data).reply()
            reply.header.rcode = 2  # Server Failure
            return reply.pack()

    def _handle_a(self, reply, conditions: QueryConditions):
        nodes = self._get_nodes(conditions)
        count = 0
        for node in nodes:
            for addr in node.addresses:
                if addr.type == AddressType.IPv4:
                    try:
                        reply.add_answer(RR(
                            rname=reply.q.qname,
                            rtype=QTYPE.A,
                            ttl=self.ttl,
                            rdata=A(addr.ip)
                        ))
                        count += 1
                        if count >= conditions.num_results:
                            return
                    except:
                        continue

    def _handle_aaaa(self, reply, conditions: QueryConditions):
        nodes = self._get_nodes(conditions)
        count = 0
        for node in nodes:
            for addr in node.addresses:
                if addr.type == AddressType.IPv6:
                    try:
                        reply.add_answer(RR(
                            rname=reply.q.qname,
                            rtype=QTYPE.AAAA,
                            ttl=self.ttl,
                            rdata=AAAA(addr.ip)
                        ))
                        count += 1
                        if count >= conditions.num_results:
                            return
                    except:
                        continue

    def _handle_srv(self, reply, conditions: QueryConditions):
        nodes = self._get_nodes(conditions)
        for node in nodes:
            for addr in node.addresses:
                if addr.type in (AddressType.IPv4, AddressType.IPv6):
                    reply.add_answer(RR(
                        rname=reply.q.qname,
                        rtype=QTYPE.SRV,
                        ttl=self.ttl,
                        rdata=SRV(0, 1, addr.port, f"{addr.ip.replace('.', '-')}.node.local.")
                    ))

    def _get_nodes(self, conditions: QueryConditions):
        if conditions.is_node_query and conditions.node_id:
            node = self.store.get_node_by_id(conditions.node_id)
            return [node] if node else []
        
        return self.store.get_random_active_nodes(
            conditions.num_results, 
            conditions.address_type
        )