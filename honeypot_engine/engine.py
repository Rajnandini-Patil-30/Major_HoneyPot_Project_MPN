"""
Multi-Service Honeypot Engine
Central runner for all protocol honeypots
"""

import logging
import time
import signal
import os
import yaml
from honeypot_engine.ssh_honeypot import SSHHoneypot
from honeypot_engine.http_honeypot import HTTPHoneypot
from honeypot_engine.ftp_honeypot import FTPHoneypot
from honeypot_engine.telnet_honeypot import TelnetHoneypot
from database.connection import init_db

logger = logging.getLogger(__name__)


class HoneypotEngine:
    """Main honeypot engine managing all protocol services"""
    
    def __init__(self, config_path: str = "./config/config.yaml"):
        """
        Initialize honeypot engine
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.services = []
        self.running = False
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def initialize(self):
        """Initialize database and services"""
        logger.info("Initializing HoneyShield Honeypot Engine...")
        
        # Initialize database
        db_config = self.config.get('database', {})
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            init_db(db_type='sqlite', db_path=db_config.get('path', './honeypot.db'))
        else:
            init_db(
                db_type='postgresql',
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                database=db_config.get('database', 'honeypot_db'),
                user=db_config.get('user', 'honeypot_user'),
                password=db_config.get('password', '')
            )
        
        logger.info("Database initialized successfully")
    
    def start_services(self):
        """Start all enabled honeypot services"""
        services_config = self.config.get('services', {})
        
        # SSH Service
        if services_config.get('ssh', {}).get('enabled', True):
            ssh_config = services_config['ssh']
            ssh = SSHHoneypot(
                host=ssh_config.get('host', '0.0.0.0'),
                port=ssh_config.get('port', 2222),
                banner=ssh_config.get('banner', 'SSH-2.0-OpenSSH_7.4'),
                max_connections=ssh_config.get('max_connections', 10)
            )
            ssh.start()
            self.services.append(ssh)
            logger.info("SSH honeypot started")
        
        # HTTP Service
        if services_config.get('http', {}).get('enabled', True):
            http_config = services_config['http']
            http = HTTPHoneypot(
                host=http_config.get('host', '0.0.0.0'),
                port=http_config.get('port', 8080),
                max_connections=http_config.get('max_connections', 10)
            )
            http.start()
            self.services.append(http)
            logger.info("HTTP honeypot started")
        
        # FTP Service
        if services_config.get('ftp', {}).get('enabled', True):
            ftp_config = services_config['ftp']
            ftp = FTPHoneypot(
                host=ftp_config.get('host', '0.0.0.0'),
                port=ftp_config.get('port', 2121),
                banner=ftp_config.get('banner', '220 FTP Server Ready'),
                max_connections=ftp_config.get('max_connections', 10)
            )
            ftp.start()
            self.services.append(ftp)
            logger.info("FTP honeypot started")
        
        # Telnet Service
        if services_config.get('telnet', {}).get('enabled', True):
            telnet_config = services_config['telnet']
            telnet = TelnetHoneypot(
                host=telnet_config.get('host', '0.0.0.0'),
                port=telnet_config.get('port', 2323),
                banner=telnet_config.get('banner', 'Welcome to HoneyShield Telnet Server'),
                max_connections=telnet_config.get('max_connections', 10)
            )
            telnet.start()
            self.services.append(telnet)
            logger.info("Telnet honeypot started")
    
    def run(self):
        """Run the honeypot engine"""
        try:
            self.running = True
            logger.info("HoneyShield Honeypot Engine running. Press Ctrl+C to stop.")
            
            # Keep running
            while self.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Shutdown signal received")
                    break
        
        except Exception as e:
            logger.error(f"Error in honeypot engine: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop all services"""
        logger.info("Stopping HoneyShield Honeypot Engine...")
        self.running = False
        
        for service in self.services:
            try:
                service.stop()
            except Exception as e:
                logger.error(f"Error stopping service: {e}")
        
        logger.info("All services stopped")


def setup_logging(log_level: str = "INFO", log_file: str = "./logs/honeypot.log"):
    """Setup logging configuration"""
    import os
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="INFO")
    
    # Create and run engine
    engine = HoneypotEngine(config_path="./config/config.yaml")
    engine.initialize()
    engine.start_services()
    engine.run()
