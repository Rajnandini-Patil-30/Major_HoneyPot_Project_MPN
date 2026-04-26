"""
FTP Honeypot Service
Simulates FTP server to capture login attempts
"""

import socket
import logging
import uuid
from honeypot_engine.base_service import BaseHoneypotService
from database.models import Session
from database.connection import get_db_manager
from datetime import datetime

logger = logging.getLogger(__name__)


class FTPHoneypot(BaseHoneypotService):
    """FTP Honeypot Service"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 2121, 
                 banner: str = "220 FTP Server Ready", max_connections: int = 10):
        """Initialize FTP honeypot"""
        super().__init__(host, port, "FTP", banner, max_connections)
    
    async def handle_connection(self, client_socket: socket.socket, client_address: tuple):
        """Handle FTP connection"""
        attacker_ip = client_address[0]
        source_port = client_address[1]
        session_id = str(uuid.uuid4())
        
        logger.info(f"FTP connection from {attacker_ip}:{source_port}")
        
        # Create session record
        try:
            db_manager = get_db_manager()
            with db_manager.get_db_session() as db_session:
                session_record = Session(
                    session_id=session_id,
                    ip=attacker_ip,
                    protocol="FTP",
                    start_time=datetime.utcnow()
                )
                db_session.add(session_record)
                db_session.commit()
        except Exception as e:
            logger.error(f"Error creating FTP session: {e}")
        
        # FTP state machine
        username = None
        authenticated = False
        
        try:
            # Send banner
            client_socket.sendall(f"{self.banner}\r\n".encode())
            
            while True:
                try:
                    # Receive command with timeout
                    client_socket.settimeout(30)
                    data = client_socket.recv(1024)
                    
                    if not data:
                        break
                    
                    command = data.decode('utf-8', errors='ignore').strip()
                    logger.debug(f"FTP command from {attacker_ip}: {command[:50]}")
                    
                    # Parse FTP commands
                    parts = command.split(' ', 1)
                    cmd = parts[0].upper()
                    arg = parts[1] if len(parts) > 1 else ""
                    
                    if cmd == "USER":
                        username = arg
                        self.log_attack_event(attacker_ip, username=username, success=False, session_id=session_id)
                        client_socket.sendall(b"331 Please specify the password.\r\n")
                    
                    elif cmd == "PASS":
                        password = arg
                        # Log credential attempt
                        if username:
                            self.log_attack_event(
                                attacker_ip,
                                username=username,
                                password=password,
                                success=False,
                                session_id=session_id
                            )
                        # Always reject
                        client_socket.sendall(b"530 Login incorrect.\r\n")
                        authenticated = False
                    
                    elif cmd == "SYST":
                        client_socket.sendall(b"215 UNIX Type: L8\r\n")
                    
                    elif cmd == "LIST":
                        client_socket.sendall(b"150 Here comes the directory listing.\r\n")
                        client_socket.sendall(b"-rw-r--r-- 1 root root 1234 Jan 01 12:00 test.txt\r\n")
                        client_socket.sendall(b"226 Directory send OK.\r\n")
                    
                    elif cmd == "QUIT":
                        client_socket.sendall(b"221 Goodbye.\r\n")
                        break
                    
                    elif cmd in ["TYPE", "PASV", "PORT", "RETR", "STOR"]:
                        client_socket.sendall(b"530 Please login with USER and PASS.\r\n")
                    
                    else:
                        client_socket.sendall(b"500 Syntax error, command unrecognized.\r\n")
                
                except socket.timeout:
                    break
                except Exception as e:
                    logger.debug(f"FTP command error from {attacker_ip}: {e}")
                    break
        
        except Exception as e:
            logger.debug(f"FTP connection error: {e}")
        
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
                logger.error(f"Error updating FTP session: {e}")
