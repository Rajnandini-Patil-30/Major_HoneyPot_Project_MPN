"""
SSH Honeypot Service
Simulates OpenSSH server to capture SSH login attempts
"""

import socket
import logging
import threading
import uuid
import time
from paramiko import Transport, ServerInterface, RSAKey, AutoAddPolicy
from io import StringIO
from honeypot_engine.base_service import BaseHoneypotService
from database.models import Credential, Command, Session
from database.connection import get_db_manager
from datetime import datetime

logger = logging.getLogger(__name__)


class SSHServerInterface(ServerInterface):
    """SSH server interface for Paramiko"""
    
    def __init__(self, attacker_ip: str, session_id: str):
        self.attacker_ip = attacker_ip
        self.session_id = session_id
        self.username = None
        self.password = None
        self.authenticated = False
        self.event_to_wait_on = None
    
    def check_auth_password(self, username, password):
        """Check authentication with password"""
        self.username = username
        self.password = password
        
        # Log credential attempt
        self._log_credential(username, password, False)
        
        # Always reject to prevent real access
        return 2  # AUTH_FAILED
    
    def check_auth_none(self, username):
        """Handle none authentication"""
        return 1  # AUTH_FAILED
    
    def check_auth_publickey(self, username, key):
        """Handle public key authentication"""
        return 1  # AUTH_FAILED
    
    def get_allowed_auths(self, username):
        """List allowed auth methods"""
        return "password"
    
    def check_channel_request(self, kind, chanid):
        """Handle channel requests"""
        if kind == "session":
            return 0  # OPEN_SUCCEEDED
        return 1  # OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_channel_shell_request(self, channel):
        """Handle shell request"""
        return 1  # OPEN_FAILED
    
    def check_channel_exec_request(self, channel, command):
        """Handle command execution request"""
        return 1  # OPEN_FAILED
    
    def get_banner(self):
        """Return banner"""
        return ("OpenSSH_7.4 Banner", "")
    
    def check_channel_subsystem_request(self, channel, name):
        """Handle subsystem request"""
        return 1  # OPEN_FAILED
    
    def _log_credential(self, username: str, password: str, success: bool):
        """Log credential attempt to database"""
        try:
            db_manager = get_db_manager()
            with db_manager.get_db_session() as session:
                cred = Credential(
                    event_id=None,  # Will be associated with event
                    username=username,
                    password=password
                )
                session.add(cred)
                session.commit()
        except Exception as e:
            logger.error(f"Error logging SSH credential: {e}")


class SSHHoneypot(BaseHoneypotService):
    """SSH Honeypot Service"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 2222, 
                 banner: str = "SSH-2.0-OpenSSH_7.4", max_connections: int = 10):
        """Initialize SSH honeypot"""
        super().__init__(host, port, "SSH", banner, max_connections)
        self.host_key = self._generate_host_key()
        
    def _generate_host_key(self):
        """Generate or load host RSA key"""
        try:
            # For demo, generate a temporary key
            # In production, load from file
            key = RSAKey.generate(1024)
            logger.info("SSH host key generated")
            return key
        except Exception as e:
            logger.error(f"Error generating SSH host key: {e}")
            return None
    
    async def handle_connection(self, client_socket: socket.socket, client_address: tuple):
        """Handle SSH connection"""
        attacker_ip = client_address[0]
        source_port = client_address[1]
        session_id = str(uuid.uuid4())
        
        logger.info(f"SSH connection from {attacker_ip}:{source_port}")
        
        # Create session record
        try:
            db_manager = get_db_manager()
            with db_manager.get_db_session() as db_session:
                session_record = Session(
                    session_id=session_id,
                    ip=attacker_ip,
                    protocol="SSH",
                    start_time=datetime.utcnow()
                )
                db_session.add(session_record)
                db_session.commit()
        except Exception as e:
            logger.error(f"Error creating SSH session record: {e}")
        
        try:
            # Setup SSH transport
            transport = Transport(client_socket)
            transport.add_server_key(self.host_key)
            
            ssh_server = SSHServerInterface(attacker_ip, session_id)
            
            # Start server with event for synchronization
            event = threading.Event()
            transport.start_server(server=ssh_server, event=event)
            
            # Wait for authentication attempt
            if not event.wait(timeout=5):
                logger.debug("SSH authentication timeout")
            
            # Wait for activity
            try:
                # Give the client some time to attempt authentication
                for _ in range(20):
                    if transport.is_active():
                        time.sleep(0.1)
                    else:
                        break
            except:
                pass
            
            # Log SSH attempt
            self.log_attack_event(
                attacker_ip,
                username=ssh_server.username,
                password=ssh_server.password,
                success=False,
                session_id=session_id
            )
            
        except Exception as e:
            logger.debug(f"SSH connection error (expected): {e}")
            self.log_attack_event(
                attacker_ip,
                username=getattr(ssh_server, 'username', None),
                password=getattr(ssh_server, 'password', None),
                success=False,
                session_id=session_id
            )
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
                logger.error(f"Error updating SSH session: {e}")
