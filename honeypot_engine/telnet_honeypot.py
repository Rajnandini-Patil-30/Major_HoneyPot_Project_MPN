"""
Telnet Honeypot Service
Simulates legacy Telnet server to capture login attempts
"""

import socket
import logging
import uuid
from honeypot_engine.base_service import BaseHoneypotService
from database.models import Session
from database.connection import get_db_manager
from datetime import datetime

logger = logging.getLogger(__name__)


class TelnetHoneypot(BaseHoneypotService):
    """Telnet Honeypot Service"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 2323,
                 banner: str = "Welcome to HoneyShield Telnet Server", max_connections: int = 10):
        """Initialize Telnet honeypot"""
        super().__init__(host, port, "Telnet", banner, max_connections)
    
    async def handle_connection(self, client_socket: socket.socket, client_address: tuple):
        """Handle Telnet connection"""
        attacker_ip = client_address[0]
        source_port = client_address[1]
        session_id = str(uuid.uuid4())
        
        logger.info(f"Telnet connection from {attacker_ip}:{source_port}")
        
        # Create session record
        try:
            db_manager = get_db_manager()
            with db_manager.get_db_session() as db_session:
                session_record = Session(
                    session_id=session_id,
                    ip=attacker_ip,
                    protocol="Telnet",
                    start_time=datetime.utcnow()
                )
                db_session.add(session_record)
                db_session.commit()
        except Exception as e:
            logger.error(f"Error creating Telnet session: {e}")
        
        # Telnet state machine
        username = None
        authenticated = False
        attempt_count = 0
        
        try:
            # Send banner
            client_socket.sendall(f"\r\n{self.banner}\r\n".encode())
            
            # Login loop
            while attempt_count < 3:  # Limit attempts
                try:
                    client_socket.settimeout(30)
                    
                    # Request username
                    client_socket.sendall(b"login: ")
                    username_data = client_socket.recv(1024)
                    username = username_data.decode('utf-8', errors='ignore').strip()
                    
                    if not username:
                        break
                    
                    # Request password
                    client_socket.sendall(b"Password: ")
                    password_data = client_socket.recv(1024)
                    password = password_data.decode('utf-8', errors='ignore').strip()
                    
                    # Log credential attempt
                    self.log_attack_event(
                        attacker_ip,
                        username=username,
                        password=password,
                        success=False,
                        session_id=session_id
                    )
                    
                    logger.info(f"Telnet login attempt: {username} from {attacker_ip}")
                    
                    # Reject login
                    client_socket.sendall(b"\r\nLogin incorrect.\r\n\r\n")
                    attempt_count += 1
                
                except socket.timeout:
                    logger.debug(f"Telnet timeout from {attacker_ip}")
                    break
                except Exception as e:
                    logger.debug(f"Telnet command error: {e}")
                    break
            
            # Send message after failed attempts
            if attempt_count > 0:
                client_socket.sendall(b"Connection closed.\r\n")
        
        except Exception as e:
            logger.debug(f"Telnet connection error: {e}")
        
        finally:
            # Update session end time
            try:
                db_manager = get_db_manager()
                with db_manager.get_db_session() as db_session:
                    session_record = db_session.query(Session).filter_by(session_id=session_id).first()
                    if session_record:
                        session_record.end_time = datetime.utcnow()
                        duration = (session_record.end_time - session_record.start_time).total_seconds()
                        session_record.duration_seconds = int(duration)
                        db_session.commit()
            except Exception as e:
                logger.error(f"Error updating Telnet session: {e}")
