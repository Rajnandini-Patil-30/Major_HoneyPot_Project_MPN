"""
HTTP Honeypot Service
Simulates web server to capture HTTP requests and payloads
"""

import socket
import logging
import threading
import uuid
from honeypot_engine.base_service import BaseHoneypotService
from database.models import HTTPRequest, Session
from database.connection import get_db_manager
from datetime import datetime
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class HTTPHoneypot(BaseHoneypotService):
    """HTTP Honeypot Service"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, max_connections: int = 10):
        """Initialize HTTP honeypot"""
        super().__init__(host, port, "HTTP", "", max_connections)
        self.fake_response = """HTTP/1.1 200 OK\r
Content-Type: text/html\r
Content-Length: 154\r
Connection: close\r
\r
<html>
<head><title>HoneyShield</title></head>
<body>
<h1>Welcome to HoneyShield</h1>
<p>This is a honeypot server. All activity is logged.</p>
</body>
</html>"""
        
        self.error_response = """HTTP/1.1 404 Not Found\r
Content-Type: text/html\r
Content-Length: 100\r
Connection: close\r
\r
<html>
<head><title>404 Not Found</title></head>
<body>
<h1>404 - Not Found</h1>
</body>
</html>"""
    
    async def handle_connection(self, client_socket: socket.socket, client_address: tuple):
        """Handle HTTP connection"""
        attacker_ip = client_address[0]
        source_port = client_address[1]
        session_id = str(uuid.uuid4())
        
        logger.info(f"HTTP connection from {attacker_ip}:{source_port}")
        
        # Create session record
        try:
            db_manager = get_db_manager()
            with db_manager.get_db_session() as db_session:
                session_record = Session(
                    session_id=session_id,
                    ip=attacker_ip,
                    protocol="HTTP",
                    start_time=datetime.utcnow()
                )
                db_session.add(session_record)
                db_session.commit()
        except Exception as e:
            logger.error(f"Error creating HTTP session: {e}")
        
        try:
            # Receive HTTP request
            http_request = b""
            while True:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    http_request += data
                    
                    # Check if we have complete headers
                    if b"\r\n\r\n" in http_request:
                        break
                except socket.timeout:
                    break
            
            # Parse HTTP request
            if http_request:
                try:
                    request_str = http_request.decode('utf-8', errors='ignore')
                    lines = request_str.split('\r\n')
                    
                    if lines and lines[0]:
                        # Parse request line
                        request_line = lines[0].split()
                        if len(request_line) >= 2:
                            method = request_line[0]
                            path = request_line[1]
                            
                            # Extract query string
                            parsed_url = urlparse(path)
                            path = parsed_url.path
                            query_string = parsed_url.query
                            
                            # Extract User-Agent and real attacker IP from reverse-proxy headers
                            user_agent = ""
                            real_ip = None
                            for line in lines[1:]:
                                low = line.lower()
                                if low.startswith("user-agent:"):
                                    user_agent = line.split(":", 1)[1].strip()
                                elif low.startswith("x-forwarded-for:"):
                                    real_ip = line.split(":", 1)[1].strip().split(",")[0].strip()
                                elif low.startswith("x-real-ip:") and not real_ip:
                                    real_ip = line.split(":", 1)[1].strip()
                            if real_ip:
                                attacker_ip = real_ip

                            # Log AttackEvent FIRST so HTTPRequest has a valid event_id
                            evt_id = self.log_attack_event(attacker_ip, session_id=session_id)

                            # Log HTTP request details tied to the event
                            self._log_http_request(
                                evt_id,
                                method,
                                path,
                                query_string,
                                user_agent,
                                http_request.decode('utf-8', errors='ignore'),
                                session_id
                            )

                            logger.info(f"HTTP {method} {path} from {attacker_ip}")

                            # Send response (404 for probes, 200 for root)
                            if path in ["/", "/index.html", "/index.htm"]:
                                response = self.fake_response
                            else:
                                response = self.error_response

                            client_socket.sendall(response.encode())

                except Exception as e:
                    logger.error(f"Error parsing HTTP request: {e}")
            
        except Exception as e:
            logger.debug(f"HTTP connection error: {e}")
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
                logger.error(f"Error updating HTTP session: {e}")
    
    def _log_http_request(self, event_id, method: str, path: str, query_string: str = "",
                         user_agent: str = "", payload: str = "", session_id: str = ""):
        """Log HTTP request to database, tied to an AttackEvent."""
        if event_id is None:
            logger.debug("Skipping HTTPRequest row: no event_id")
            return
        try:
            db_manager = get_db_manager()
            with db_manager.get_db_session() as session:
                http_req = HTTPRequest(
                    event_id=event_id,
                    method=method,
                    path=path,
                    query_string=query_string,
                    user_agent=user_agent,
                    payload=payload,
                    response_code=404 if path not in ["/", "/index.html"] else 200
                )
                session.add(http_req)
                session.commit()
                logger.debug(f"HTTP request logged: {method} {path}")
        except Exception as e:
            logger.error(f"Error logging HTTP request: {e}")
