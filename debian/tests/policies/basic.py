from Zorp.Core import *
from Zorp.Plug import *
from Zorp.Http import *
from Zorp.Ftp import *


		
InetZone("local", "127.0.0.0/8",
         inbound_services=["*"],
         outbound_services=["*"])
        
InetZone("internet", "0.0.0.0/0",
         inbound_services=[],
         outbound_services=[])


def zorp():
    Service("test", PlugProxy, router=DirectedRouter(SockAddrInet("127.0.0.2", 50081)))
    Listener(SockAddrInet("127.0.0.2", 50080), "test")
