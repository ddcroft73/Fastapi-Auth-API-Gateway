import socket
#from app.utils.api_logger import logzz

def get_host_ip2():
    try:
        # The following line creates a new socket and connects to an external 
        # address (in this case, one of Google's public DNS servers). 
        # We don't actually send any data or rely on this connection; 
        # we're just using it to determine the most appropriate network interface 
        # and its associated IP address.
        s = socket.create_connection(("8.8.8.8", 80), timeout=5)
        ip_address = s.getsockname()[0]
        s.close()
        print(ip_address)
        return ip_address
    except Exception as e:
        print(f"Failed to get host IP: {e}")
        return None
import socket

def get_host_ip():
    try:
        # This uses a UDP connection (which is connectionless and doesn't actually establish a connection)
        # to determine the most appropriate network interface.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"Failed to get host IP: {e}")
        return None

print(get_host_ip())