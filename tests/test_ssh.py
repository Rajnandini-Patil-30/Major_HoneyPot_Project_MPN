"""
SSH Honeypot Test Script
Tests SSH brute-force and credential capture
"""

import paramiko
import socket
import time
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSHBruteForcer:
    """SSH brute-force tester"""
    
    def __init__(self, target_host: str, target_port: int = 2222, timeout: int = 5):
        """Initialize SSH brute-forcer"""
        self.target_host = target_host
        self.target_port = target_port
        self.timeout = timeout
        self.attempts = 0
        self.successes = 0
        self.failures = 0
    
    def test_credential(self, username: str, password: str) -> bool:
        """Test single credential"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            logger.info(f"Attempting SSH login: {username}:{password}")
            
            client.connect(
                self.target_host,
                port=self.target_port,
                username=username,
                password=password,
                timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False
            )
            
            logger.info(f"Success: {username}:{password}")
            self.successes += 1
            client.close()
            return True
            
        except paramiko.AuthenticationException:
            logger.info(f"Failed: {username}:{password}")
            self.failures += 1
            return False
        
        except Exception as e:
            logger.debug(f"SSH connection error: {e}")
            self.failures += 1
            return False
    
    def run_test(self, credentials: List[Tuple[str, str]]):
        """Run brute-force test with credential list"""
        logger.info(f"Starting SSH brute-force test on {self.target_host}:{self.target_port}")
        logger.info(f"Testing {len(credentials)} credentials...")
        
        for username, password in credentials:
            self.test_credential(username, password)
            self.attempts += 1
            time.sleep(0.5)  # Small delay between attempts
        
        logger.info(f"SSH test complete: {self.attempts} attempts, {self.successes} successes, {self.failures} failures")


def main():
    """Run SSH test"""
    # Common credentials to test
    credentials = [
        ("root", "root"),
        ("root", "password"),
        ("root", "123456"),
        ("admin", "admin"),
        ("admin", "password"),
        ("admin", "123456"),
        ("user", "user"),
        ("user", "password"),
        ("test", "test"),
        ("www-data", "www-data"),
    ]
    
    # Target configuration
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost", help="Honeypot host (default: localhost)")
    ap.add_argument("--port", type=int, default=2222, help="SSH honeypot port (default: 2222)")
    args = ap.parse_args()
    target_host = args.host
    target_port = args.port
    
    # Run test
    tester = SSHBruteForcer(target_host, target_port)
    tester.run_test(credentials)


if __name__ == "__main__":
    main()
