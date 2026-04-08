from bech32 import bech32_decode, convertbits
from .types import QueryConditions


def parse_conditions(subdomain: str) -> QueryConditions:
    q = QueryConditions()

    parts = [p for p in subdomain.split('.') if p]

    for part in reversed(parts):
        if len(part) < 2:
            continue

        key = part[0].lower()
        value = part[1:]

        if key == 'r' and len(value) == 1:
            q.realm = ord(value)
        elif key == 'a':
            try:
                q.address_type = int(value)
            except ValueError:
                pass
        elif key == 'n':
            try:
                num = int(value)
                q.num_results = min(max(num, 1), 50)   # ограничение
            except ValueError:
                pass
        elif key == 'l':
            # bech32 node id
            decoded = bech32_decode(value)
            if decoded:
                hrp, data5 = decoded
                data8 = convertbits(data5, 5, 8, False)
                if data8:
                    q.node_id = bytes(data8)
                    q.is_node_query = True

    return q