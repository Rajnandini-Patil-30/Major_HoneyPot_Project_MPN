"""
HoneyShield Dashboard Backend API
FastAPI server providing REST endpoints for the dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import os
from database.connection import init_db, get_db_manager
from database.models import AttackEvent, Credential, Command, Session, HTTPRequest, GeoData
from sqlalchemy import func, desc, cast, String

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HoneyShield Dashboard API",
    description="REST API for HoneyShield honeypot intelligence platform",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AttackEventSchema(BaseModel):
    id: int
    timestamp: datetime
    ip: str
    protocol: str
    port: int
    success: bool
    session_id: Optional[str]
    
    class Config:
        from_attributes = True


class CredentialSchema(BaseModel):
    username: str
    password: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class SessionSchema(BaseModel):
    session_id: str
    ip: str
    protocol: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    event_count: int
    
    class Config:
        from_attributes = True


class AttackerSchema(BaseModel):
    ip: str
    count: int
    country: Optional[str]
    city: Optional[str]


class DashboardStatsSchema(BaseModel):
    total_events: int
    total_sessions: int
    unique_attackers: int
    by_protocol: dict
    events_last_24h: int


# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Initialize database on app startup"""
    db_type = os.getenv("DB_TYPE", "sqlite")
    
    if db_type == "sqlite":
        db_path = os.getenv("DB_PATH", "./honeypot.db")
        init_db(db_type="sqlite", db_path=db_path)
    else:
        init_db(
            db_type="postgresql",
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "honeypot_db"),
            user=os.getenv("DB_USER", "honeypot_user"),
            password=os.getenv("DB_PASSWORD", "")
        )
    
    logger.info("Dashboard backend initialized")


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Statistics endpoints
@app.get("/api/stats", response_model=DashboardStatsSchema)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            total_events = session.query(func.count(AttackEvent.id)).scalar() or 0
            total_sessions = session.query(func.count(Session.id)).scalar() or 0
            unique_attackers = session.query(func.count(func.distinct(AttackEvent.ip))).scalar() or 0
            
            # Events by protocol
            protocol_counts = session.query(
                AttackEvent.protocol,
                func.count(AttackEvent.id)
            ).group_by(AttackEvent.protocol).all()
            
            by_protocol = {protocol: count for protocol, count in protocol_counts}
            
            # Events in last 24 hours
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            events_last_24h = session.query(
                func.count(AttackEvent.id)
            ).filter(AttackEvent.timestamp >= twenty_four_hours_ago).scalar() or 0
            
            return DashboardStatsSchema(
                total_events=total_events,
                total_sessions=total_sessions,
                unique_attackers=unique_attackers,
                by_protocol=by_protocol,
                events_last_24h=events_last_24h
            )
    
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Error fetching statistics")


# Attack events endpoints
@app.get("/api/events", response_model=List[AttackEventSchema])
async def get_attack_events(
    protocol: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get attack events with optional filtering"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            query = session.query(AttackEvent)
            
            if protocol:
                query = query.filter(AttackEvent.protocol == protocol)
            
            events = query.order_by(desc(AttackEvent.timestamp)).offset(skip).limit(limit).all()
            return events
    
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail="Error fetching events")


# Top attackers endpoint
@app.get("/api/attackers", response_model=List[AttackerSchema])
async def get_top_attackers(limit: int = 10):
    """Get top attacking IPs"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            top_ips = session.query(
                AttackEvent.ip,
                func.count(AttackEvent.id).label("count")
            ).group_by(AttackEvent.ip).order_by(
                func.count(AttackEvent.id).desc()
            ).limit(limit).all()
            
            results = []
            for ip, count in top_ips:
                # Get geo data if available
                geo = session.query(GeoData).filter(GeoData.ip == ip).first()
                results.append(AttackerSchema(
                    ip=ip,
                    count=count,
                    country=geo.country if geo else None,
                    city=geo.city if geo else None
                ))
            
            return results
    
    except Exception as e:
        logger.error(f"Error fetching attackers: {e}")
        raise HTTPException(status_code=500, detail="Error fetching attackers")


# Credentials endpoint
@app.get("/api/credentials", response_model=List[dict])
async def get_top_credentials(limit: int = 10):
    """Get most attempted credentials"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            top_creds = session.query(
                Credential.username,
                Credential.password,
                func.count(Credential.id).label("count")
            ).group_by(
                Credential.username,
                Credential.password
            ).order_by(
                func.count(Credential.id).desc()
            ).limit(limit).all()
            
            return [
                {
                    "username": username,
                    "password": password,
                    "count": count
                }
                for username, password, count in top_creds
            ]
    
    except Exception as e:
        logger.error(f"Error fetching credentials: {e}")
        raise HTTPException(status_code=500, detail="Error fetching credentials")


# Sessions endpoint
@app.get("/api/sessions", response_model=List[SessionSchema])
async def get_sessions(protocol: Optional[str] = None, skip: int = 0, limit: int = 50):
    """Get attack sessions"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            query = session.query(Session)
            
            if protocol:
                query = query.filter(Session.protocol == protocol)
            
            sessions_data = query.order_by(desc(Session.start_time)).offset(skip).limit(limit).all()
            return sessions_data
    
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching sessions")


# Protocol distribution endpoint
@app.get("/api/protocol-distribution")
async def get_protocol_distribution():
    """Get attack distribution by protocol"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            distribution = session.query(
                AttackEvent.protocol,
                func.count(AttackEvent.id).label("count")
            ).group_by(AttackEvent.protocol).all()
            
            return {
                protocol: count
                for protocol, count in distribution
            }
    
    except Exception as e:
        logger.error(f"Error fetching protocol distribution: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data")


# Geo distribution endpoint
@app.get("/api/geo-distribution")
async def get_geo_distribution():
    """Get attack distribution by country"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            distribution = session.query(
                GeoData.country,
                func.count(GeoData.id).label("count")
            ).group_by(GeoData.country).order_by(
                func.count(GeoData.id).desc()
            ).limit(20).all()
            
            return {
                country: count
                for country, count in distribution
                if country
            }
    
    except Exception as e:
        logger.error(f"Error fetching geo distribution: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data")


# Timeline endpoint
@app.get("/api/timeline")
async def get_attack_timeline(hours: int = 24):
    """Get attack timeline for last N hours"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            from sqlalchemy import func
            hour_expr = func.strftime('%Y-%m-%d %H:00:00', AttackEvent.timestamp).label("hour")
            timeline = session.query(
                hour_expr,
                func.count(AttackEvent.id).label("count")
            ).filter(
                AttackEvent.timestamp >= cutoff
            ).group_by("hour").order_by("hour").all()
            
            return [
                {"hour": str(hour), "count": count}
                for hour, count in timeline
            ]
    
    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data")


# Geo map endpoint — returns lat/lon coordinates for Leaflet map pins
@app.get("/api/geo-map")
async def get_geo_map():
    """Get geo data with coordinates for world map rendering"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            # Join GeoData with AttackEvent to get protocol and count per IP
            results = session.query(
                GeoData.ip,
                GeoData.latitude,
                GeoData.longitude,
                GeoData.country,
                GeoData.city,
                func.count(AttackEvent.id).label("count"),
                func.max(AttackEvent.timestamp).label("last_seen"),
            ).join(
                AttackEvent, AttackEvent.ip == GeoData.ip
            ).filter(
                GeoData.latitude != 0.0,
                GeoData.longitude != 0.0
            ).group_by(
                GeoData.ip, GeoData.latitude, GeoData.longitude,
                GeoData.country, GeoData.city
            ).order_by(desc("count")).limit(100).all()

            return [
                {
                    "ip": ip,
                    "latitude": lat,
                    "longitude": lon,
                    "country": country or "Unknown",
                    "city": city or "Unknown",
                    "count": count,
                    "last_seen": str(last_seen) if last_seen else None,
                }
                for ip, lat, lon, country, city, count, last_seen in results
            ]

    except Exception as e:
        logger.error(f"Error fetching geo map data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching geo map data")


# Commands endpoint — all captured commands
@app.get("/api/commands")
async def get_commands(limit: int = 50):
    """Get captured attacker commands"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            cmds = session.query(
                Command.command,
                func.count(Command.id).label("count")
            ).group_by(Command.command).order_by(
                func.count(Command.id).desc()
            ).limit(limit).all()

            return [
                {"command": cmd, "count": count}
                for cmd, count in cmds
            ]

    except Exception as e:
        logger.error(f"Error fetching commands: {e}")
        raise HTTPException(status_code=500, detail="Error fetching commands")


# HTTP requests endpoint
@app.get("/api/http-requests")
async def get_http_requests(limit: int = 50):
    """Get captured HTTP requests"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            reqs = session.query(HTTPRequest).order_by(
                desc(HTTPRequest.timestamp)
            ).limit(limit).all()

            return [
                {
                    "method": r.method,
                    "path": r.path,
                    "user_agent": r.user_agent,
                    "payload": r.payload,
                    "timestamp": str(r.timestamp) if r.timestamp else None,
                }
                for r in reqs
            ]

    except Exception as e:
        logger.error(f"Error fetching HTTP requests: {e}")
        raise HTTPException(status_code=500, detail="Error fetching HTTP requests")


# Protocols list endpoint
@app.get("/api/protocols")
async def get_protocols():
    """Get list of active protocols with counts"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            protocols = session.query(
                AttackEvent.protocol,
                func.count(AttackEvent.id).label("count")
            ).group_by(AttackEvent.protocol).all()

            return [
                {"protocol": proto, "count": count}
                for proto, count in protocols
            ]

    except Exception as e:
        logger.error(f"Error fetching protocols: {e}")
        raise HTTPException(status_code=500, detail="Error fetching protocols")


# Session commands endpoint — for session replay panel
@app.get("/api/sessions/{session_db_id}/commands")
async def get_session_commands(session_db_id: int):
    """Get commands for a specific session (joins Session -> AttackEvent -> Command)"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            # Get the session record
            sess = session.query(Session).filter(Session.id == session_db_id).first()
            if not sess:
                raise HTTPException(status_code=404, detail="Session not found")

            # Get all commands from events linked to this session
            cmds = session.query(Command).join(
                AttackEvent, Command.event_id == AttackEvent.id
            ).filter(
                AttackEvent.session_id == session_db_id
            ).order_by(Command.timestamp).all()

            return {
                "session_id": sess.session_id,
                "ip": sess.ip,
                "protocol": sess.protocol,
                "start_time": str(sess.start_time),
                "duration_seconds": sess.duration_seconds,
                "commands": [
                    {
                        "command": cmd.command,
                        "output": cmd.output,
                        "timestamp": str(cmd.timestamp) if cmd.timestamp else None,
                    }
                    for cmd in cmds
                ]
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session commands: {e}")
        raise HTTPException(status_code=500, detail="Error fetching session commands")


# Recent events for live feed
@app.get("/api/events/recent")
async def get_recent_events(limit: int = 20):
    """Get most recent events for live threat feed"""
    try:
        db_manager = get_db_manager()
        with db_manager.get_db_session() as session:
            events = session.query(AttackEvent).order_by(
                desc(AttackEvent.timestamp)
            ).limit(limit).all()

            results = []
            for evt in events:
                # Get credential if any
                cred = session.query(Credential).filter(
                    Credential.event_id == evt.id
                ).first()

                detail = ""
                if cred:
                    detail = f"{cred.username}:{cred.password or '***'}"
                elif evt.protocol == "HTTP":
                    http_req = session.query(HTTPRequest).filter(
                        HTTPRequest.event_id == evt.id
                    ).first()
                    if http_req:
                        detail = f"{http_req.method} {http_req.path}"

                # Get geo data
                geo = session.query(GeoData).filter(GeoData.ip == evt.ip).first()

                results.append({
                    "id": evt.id,
                    "timestamp": str(evt.timestamp),
                    "ip": evt.ip,
                    "protocol": evt.protocol,
                    "detail": detail,
                    "country": geo.country if geo else None,
                    "country_code": geo.country_code if geo else None,
                })

            return results

    except Exception as e:
        logger.error(f"Error fetching recent events: {e}")
        raise HTTPException(status_code=500, detail="Error fetching recent events")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
