"""
Base honeypot service for protocol implementations
"""

import asyncio
import logging
import socket
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from database.models import AttackEvent, Session
from database.connection import get_db_manager

logger = logging.getLogger(__name__)


class BaseHoneypotService(ABC):
    """Abstract base class for honeypot protocol services"""
    
    def __init__(self, host: str, port: int, protocol: str, banner: str = "", max_connections: int = 10):
        """
        Initialize honeypot service
        
        Args:
            host: Host to bind to
            port: Port to listen on
            protocol: Protocol name (SSH, HTTP, FTP, Telnet)
            banner: Service banner to display
            max_connections: Maximum concurrent connections
        """
        self.host = host
        self.port = port
        self.protocol = protocol
        self.banner = banner
        self.max_connections = max_connections
        self.running = False
        self.server_socket = None
        self.active_connections = 0
        self.lock = threading.Lock()
        
    @abstractmethod
    async def handle_connection(self, client_socket: socket.socket, client_address: tuple):
        """
        Handle incoming connection
        Implemented by subclasses for specific protocols
        """
        pass
    
    def start(self):
        """Start the honeypot service"""
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        logger.info(f"{self.protocol} honeypot service started on {self.host}:{self.port}")
    
    def _run(self):
        """Main service loop"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            self.running = True
            
            logger.info(f"{self.protocol} service listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    
                    with self.lock:
                        if self.active_connections >= self.max_connections:
                            logger.warning(f"{self.protocol}: Max connections reached, rejecting {client_address}")
                            client_socket.close()
                            continue
                        self.active_connections += 1
                    
                    # Handle connection in separate thread
                    handler_thread = threading.Thread(
                        target=self._handle_connection_wrapper,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    handler_thread.start()
                    
                except Exception as e:
                    if self.running:
                        logger.error(f"{self.protocol} error accepting connection: {e}")
                    
        except Exception as e:
            logger.error(f"{self.protocol} service error: {e}")
        finally:
            self.stop()
    
    def _handle_connection_wrapper(self, client_socket: socket.socket, client_address: tuple):
        """Wrapper for connection handler"""
        try:
            # Run async handler
            asyncio.run(self.handle_connection(client_socket, client_address))
        except Exception as e:
            logger.error(f"{self.protocol} connection handler error: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            
            with self.lock:
                self.active_connections -= 1
    
    def log_attack_event(self, ip: str, username: str = None, password: str = None, 
                        success: bool = False, session_id: str = None, **kwargs) -> AttackEvent:
        """
        Log an attack event to database
        
        Args:
            ip: Attacker IP
            username: Username attempted
            password: Password attempted
            success: Whether login was successful
            session_id: Session identifier
            **kwargs: Additional data
        
        Returns:
            AttackEvent object
        """
        try:
            db_manager = get_db_manager()
            with db_manager.get_db_session() as session:
                event = AttackEvent(
                    timestamp=datetime.utcnow(),
                    ip=ip,
                    protocol=self.protocol,
                    port=self.port,
                    success=success,
                    session_id=session_id,
                )
                session.add(event)
                session.flush()
                
                # Add credential if provided
                if username is not None:
                    from database.models import Credential
                    cred = Credential(
                        event_id=event.id,
                        username=username,
                        password=password
                    )
                    session.add(cred)
                
                session.commit()
                event_id = event.id
                logger.debug(f"Event logged: {self.protocol} from {ip}")

            # Enrich with geolocation (outside DB session, non-blocking on failure)
            try:
                from geo_service.geolocation import get_geo_service
                geo_svc = get_geo_service()
                geo_svc.enrich_attack_event(event_id, ip)
            except Exception as geo_err:
                logger.warning(f"Geo enrichment failed for {ip}: {geo_err}")

            return event_id

        except Exception as e:
            logger.error(f"Error logging attack event: {e}")
            return None
    
    def stop(self):
        """Stop the honeypot service"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        logger.info(f"{self.protocol} honeypot service stopped")
