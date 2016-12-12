from Zorp.Core import *
from Zorp.Plug import *
from Zorp.Http import *
from Zorp.Ftp import *
from Zorp.Dispatch import *

		
InetZone("local", "127.0.0.0/8")
        
InetZone("internet", "0.0.0.0/0")


def zorp():
    Service("test", PlugProxy, router=DirectedRouter(SockAddrInet("127.0.0.2", 50081)))
    Dispatcher(bindto=convertSockAddrToDB(SockAddrInet("127.0.0.2", 50080), ZD_PROTO_TCP), service="test")
