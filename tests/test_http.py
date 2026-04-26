"""
HTTP Honeypot Test Script
Tests HTTP probes and payload capture
"""

import requests
import logging
import time
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPTester:
    """HTTP honeypot tester"""
    
    def __init__(self, target_url: str, timeout: int = 5):
        """Initialize HTTP tester"""
        self.target_url = target_url
        self.timeout = timeout
        self.attempts = 0
        self.successes = 0
        self.failures = 0
        
        # Disable SSL verification for testing
        self.session = requests.Session()
        self.session.verify = False
    
    def send_probe(self, path: str, payload: str = None, method: str = "GET") -> bool:
        """Send HTTP probe"""
        try:
            full_url = f"{self.target_url}{path}"
            
            if payload:
                logger.info(f"Sending HTTP {method} with payload: {path}?{payload}")
            else:
                logger.info(f"Sending HTTP {method}: {path}")
            
            if method == "GET":
                response = self.session.get(full_url, params={"payload": payload} if payload else None, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(full_url, data={"payload": payload}, timeout=self.timeout)
            
            logger.info(f"Response code: {response.status_code}")
            self.successes += 1
            return True
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"HTTP request error: {e}")
            self.failures += 1
            return False
        except Exception as e:
            logger.debug(f"Error: {e}")
            self.failures += 1
            return False
    
    def run_test(self, probes: List[dict]):
        """Run HTTP test with probe list"""
        logger.info(f"Starting HTTP test on {self.target_url}")
        logger.info(f"Testing {len(probes)} probes...")
        
        for probe in probes:
            path = probe.get('path', '/')
            payload = probe.get('payload', None)
            method = probe.get('method', 'GET')
            
            self.send_probe(path, payload, method)
            self.attempts += 1
            time.sleep(0.3)  # Small delay between probes
        
        logger.info(f"HTTP test complete: {self.attempts} attempts, {self.successes} successes, {self.failures} failures")


def main():
    """Run HTTP test"""
    # Common web attack probes
    probes = [
        # Path traversal attempts
        {"path": "/../../../etc/passwd", "method": "GET"},
        {"path": "/../../etc/shadow", "method": "GET"},
        {"path": "/....//....//....//etc/passwd", "method": "GET"},
        
        # SQL injection probes
        {"path": "/search", "payload": "id=1' OR '1'='1", "method": "GET"},
        {"path": "/login", "payload": "username=admin'--", "method": "POST"},
        
        # XSS probes
        {"path": "/search", "payload": "<script>alert('xss')</script>", "method": "GET"},
        {"path": "/feedback", "payload": "comment=<img src=x onerror=alert(1)>", "method": "POST"},
        
        # Command injection
        {"path": "/ping", "payload": "host=127.0.0.1;whoami", "method": "GET"},
        
        # Common scanner probes
        {"path": "/admin", "method": "GET"},
        {"path": "/administrator", "method": "GET"},
        {"path": "/wp-admin", "method": "GET"},
        {"path": "/phpmyadmin", "method": "GET"},
        {"path": "/.env", "method": "GET"},
        {"path": "/config.php", "method": "GET"},
        {"path": "/web.config", "method": "GET"},
        
        # Common files
        {"path": "/backup.zip", "method": "GET"},
        {"path": "/database.sql", "method": "GET"},
        {"path": "/.git/config", "method": "GET"},
        
        # Root and index
        {"path": "/", "method": "GET"},
        {"path": "/index.html", "method": "GET"},
        {"path": "/index.php", "method": "GET"},
    ]
    
    # Target configuration — override with --host / --port for remote VPS testing
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost", help="Honeypot host (default: localhost)")
    ap.add_argument("--port", type=int, default=8080, help="HTTP honeypot port (default: 8080)")
    args = ap.parse_args()
    target_url = f"http://{args.host}:{args.port}"
    
    # Run test
    tester = HTTPTester(target_url)
    tester.run_test(probes)


if __name__ == "__main__":
    # Suppress SSL warnings for testing
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()
