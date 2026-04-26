"""
Telnet Honeypot Test Script
Tests Telnet login attempts
"""

import socket
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelnetTester:
    """Telnet honeypot tester"""
    
    def __init__(self, target_host: str, target_port: int = 2323, timeout: int = 5):
        """Initialize Telnet tester"""
        self.target_host = target_host
        self.target_port = target_port
        self.timeout = timeout
        self.attempts = 0
        self.successes = 0
        self.failures = 0
    
    def test_credential(self, username: str, password: str) -> bool:
        """Test single Telnet credential"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            logger.info(f"Connecting to {self.target_host}:{self.target_port}")
            sock.connect((self.target_host, self.target_port))
            
            # Receive banner
            time.sleep(0.2)
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            logger.info(f"Banner: {banner.strip()}")
            
            # Wait for login prompt
            time.sleep(0.2)
            
            # Send username
            logger.info(f"Attempting Telnet login: {username}:{password}")
            sock.sendall(f"{username}\r\n".encode())
            time.sleep(0.2)
            
            # Receive password prompt
            prompt = sock.recv(1024).decode('utf-8', errors='ignore')
            logger.info(f"Response: {prompt.strip()}")
            
            # Send password
            sock.sendall(f"{password}\r\n".encode())
            time.sleep(0.2)
            
            # Receive login result
            result = sock.recv(1024).decode('utf-8', errors='ignore')
            
            if "incorrect" in result.lower() or "fail" in result.lower():
                logger.info(f"Failed: {username}:{password}")
                self.failures += 1
            else:
                logger.info(f"Response: {result.strip()}")
                self.successes += 1
            
            sock.close()
            return True
            
        except Exception as e:
            logger.debug(f"Telnet connection error: {e}")
            self.failures += 1
            return False
    
    def run_test(self, credentials: list):
        """Run Telnet test"""
        logger.info(f"Starting Telnet test on {self.target_host}:{self.target_port}")
        logger.info(f"Testing {len(credentials)} credentials...")
        
        for username, password in credentials:
            self.test_credential(username, password)
            self.attempts += 1
            time.sleep(0.5)
        
        logger.info(f"Telnet test complete: {self.attempts} attempts, {self.successes} successes, {self.failures} failures")


def main():
    """Run Telnet test"""
    credentials = [
        ("root", "root"),
        ("admin", "admin"),
        ("user", "user"),
        ("test", "test"),
    ]
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost", help="Honeypot host (default: localhost)")
    ap.add_argument("--port", type=int, default=2323, help="Telnet honeypot port (default: 2323)")
    args = ap.parse_args()
    target_host = args.host
    target_port = args.port
    
    tester = TelnetTester(target_host, target_port)
    tester.run_test(credentials)


if __name__ == "__main__":
    main()
