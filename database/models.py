"""
Database models for HoneyShield
Define SQLAlchemy ORM models for all attack event types
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AttackEvent(Base):
    """Master event log for all attack attempts"""
    __tablename__ = "attack_events"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip = Column(String(45), nullable=False, index=True)  # IPv4 or IPv6
    protocol = Column(String(20), nullable=False)  # SSH, HTTP, FTP, Telnet, SMTP
    port = Column(Integer)
    source_port = Column(Integer)
    success = Column(Boolean, default=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)
    
    # Relationships
    credentials = relationship("Credential", back_populates="event", cascade="all, delete-orphan")
    commands = relationship("Command", back_populates="event", cascade="all, delete-orphan")
    http_requests = relationship("HTTPRequest", back_populates="event", cascade="all, delete-orphan")
    geo_data = relationship("GeoData", back_populates="event", uselist=False, cascade="all, delete-orphan")
    session = relationship("Session", back_populates="events")
    
    def __repr__(self):
        return f"<AttackEvent(ip={self.ip}, protocol={self.protocol}, timestamp={self.timestamp})>"


class Credential(Base):
    """Captured credentials from login attempts"""
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("attack_events.id"), nullable=False, index=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    event = relationship("AttackEvent", back_populates="credentials")
    
    def __repr__(self):
        return f"<Credential(username={self.username}, event_id={self.event_id})>"


class Command(Base):
    """Commands executed by attacker in shell"""
    __tablename__ = "commands"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("attack_events.id"), nullable=False, index=True)
    command = Column(Text, nullable=False)
    output = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    event = relationship("AttackEvent", back_populates="commands")
    
    def __repr__(self):
        return f"<Command(command={self.command}, event_id={self.event_id})>"


class HTTPRequest(Base):
    """HTTP requests and payloads"""
    __tablename__ = "http_requests"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("attack_events.id"), nullable=False, index=True)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE, etc.
    path = Column(Text, nullable=False)
    query_string = Column(Text)
    user_agent = Column(Text)
    payload = Column(Text)
    response_code = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    event = relationship("AttackEvent", back_populates="http_requests")
    
    def __repr__(self):
        return f"<HTTPRequest(method={self.method}, path={self.path}, event_id={self.event_id})>"


class GeoData(Base):
    """Geolocation enrichment for attacker IP"""
    __tablename__ = "geo_data"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("attack_events.id"), index=True)
    ip = Column(String(45), unique=True, index=True, nullable=False)
    country = Column(String(100))
    country_code = Column(String(2))
    city = Column(String(100))
    region = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    timezone = Column(String(100))
    isp = Column(String(255))
    asn = Column(String(20))
    cached_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    event = relationship("AttackEvent", back_populates="geo_data")
    
    def __repr__(self):
        return f"<GeoData(ip={self.ip}, country={self.country}, city={self.city})>"


class Session(Base):
    """Full session record for each attacker connection"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    ip = Column(String(45), nullable=False, index=True)
    protocol = Column(String(20), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    event_count = Column(Integer, default=0)
    successful_login = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Relationship
    events = relationship("AttackEvent", back_populates="session")
    
    def __repr__(self):
        return f"<Session(session_id={self.session_id}, ip={self.ip}, protocol={self.protocol})>"


class DashboardUser(Base):
    """Dashboard admin users"""
    __tablename__ = "dashboard_users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<DashboardUser(username={self.username})>"


class LogRetention(Base):
    """Track log retention and archival"""
    __tablename__ = "log_retention"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("attack_events.id"))
    archived = Column(Boolean, default=False)
    archive_path = Column(String(500))
    archived_at = Column(DateTime)
    
    def __repr__(self):
        return f"<LogRetention(event_id={self.event_id}, archived={self.archived})>"
