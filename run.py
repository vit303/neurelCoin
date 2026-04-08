
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import dnsseed.main
from dnsseed.types import QueryConditions, AddressType
from dnsseed.peer_store import PeerStore
from dnsseed.utils import parse_conditions

if __name__ == "__main__":
    import asyncio
    asyncio.run(dnsseed.main.main())