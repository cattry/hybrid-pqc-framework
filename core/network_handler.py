import socket
import time
import random

class NetworkHandler:
    def __init__(self, host, port, is_server=False):
        self.host = host
        self.port = port
        self.is_server = is_server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        self.address = None

    def start_connection(self):
        if self.is_server:
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            print(f"[NETWORK] Listening for incoming P2P connections on {self.host}:{self.port}...")
            self.connection, self.address = self.socket.accept()
            print(f"[NETWORK] Connection established with {self.address}")
        else:
            print(f"[NETWORK] Attempting to connect to server at {self.host}:{self.port}...")
            self.socket.connect((self.host, self.port))
            self.connection = self.socket
            self.address = (self.host, self.port)
            print(f"[NETWORK] Successfully connected to {self.address}")

    def check_latency(self):
        """
        Simulates a production latency check. 
        Large PQC payloads risk severe packet fragmentation on constrained networks.
        Returns True if the network is stable, False if it times out.
        """
        print("[SYSTEM] Pinging peer to check network constraints for PQC payloads...")
        time.sleep(0.5) # Simulate network transit time
        
        # 20% chance of simulating severe network congestion/timeout
        if random.random() < 0.2:
            print("[WARNING] Ping timeout > 2000ms. Network congested.")
            return False
        return True

    def send_data(self, data: bytes):
        if not self.connection:
            raise ConnectionError("No active connection to send data.")
        self.connection.sendall(data)

    def receive_data(self, buffer_size=4096):
        if not self.connection:
            raise ConnectionError("No active connection to receive data.")
        try:
            data = self.connection.recv(buffer_size)
            return data
        except ConnectionResetError:
            print("[NETWORK] The connection was closed by the remote peer.")
            return b""

    def close_connection(self):
        if self.connection and self.is_server:
            self.connection.close()
        self.socket.close()
        print("[NETWORK] Connection closed.")