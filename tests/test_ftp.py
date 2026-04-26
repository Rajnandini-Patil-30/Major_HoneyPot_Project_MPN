"""
FTP Honeypot Test Script
Tests FTP login attempts
"""

import socket
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FTPTester:
    """FTP honeypot tester"""
    
    def __init__(self, target_host: str, target_port: int = 2121, timeout: int = 5):
        """Initialize FTP tester"""
        self.target_host = target_host
        self.target_port = target_port
        self.timeout = timeout
        self.attempts = 0
        self.successes = 0
        self.failures = 0
    
    def send_ftp_command(self, sock: socket.socket, command: str) -> str:
        """Send FTP command and receive response"""
        try:
            sock.sendall(f"{command}\r\n".encode())
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            return response
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return ""
    
    def test_credential(self, username: str, password: str) -> bool:
        """Test single FTP credential"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            logger.info(f"Connecting to {self.target_host}:{self.target_port}")
            sock.connect((self.target_host, self.target_port))
            
            # Receive banner
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            logger.info(f"Banner: {banner.strip()}")
            
            # Send USER command
            logger.info(f"Attempting FTP login: {username}:{password}")
            self.send_ftp_command(sock, f"USER {username}")
            
            # Send PASS command
            response = self.send_ftp_command(sock, f"PASS {password}")
            
            if "530" in response or "incorrect" in response.lower():
                logger.info(f"Failed: {username}:{password}")
                self.failures += 1
                result = False
            else:
                logger.info(f"Response: {response.strip()}")
                self.successes += 1
                result = True
            
            # Send QUIT
            self.send_ftp_command(sock, "QUIT")
            sock.close()
            
            return result
            
        except Exception as e:
            logger.debug(f"FTP connection error: {e}")
            self.failures += 1
            return False
    
    def run_test(self, credentials: list):
        """Run FTP test"""
        logger.info(f"Starting FTP test on {self.target_host}:{self.target_port}")
        logger.info(f"Testing {len(credentials)} credentials...")
        
        for username, password in credentials:
            self.test_credential(username, password)
            self.attempts += 1
            time.sleep(0.5)
        
        logger.info(f"FTP test complete: {self.attempts} attempts, {self.successes} successes, {self.failures} failures")


def main():
    """Run FTP test"""
    credentials = [
        ("root", "root"),
        ("admin", "admin"),
        ("ftp", "ftp"),
        ("anonymous", ""),
        ("user", "password"),
    ]
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost", help="Honeypot host (default: localhost)")
    ap.add_argument("--port", type=int, default=2121, help="FTP honeypot port (default: 2121)")
    args = ap.parse_args()
    target_host = args.host
    target_port = args.port
    
    tester = FTPTester(target_host, target_port)
    tester.run_test(credentials)


if __name__ == "__main__":
    main()
