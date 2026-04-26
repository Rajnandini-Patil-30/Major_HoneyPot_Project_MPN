"""
Database Validation Script
Verifies that attack events are captured correctly in the database
"""

import logging
import sys
from database.connection import get_db_manager, init_db
from database.models import AttackEvent, Credential, HTTPRequest, Session
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseValidator:
    """Validates captured attack data"""
    
    def __init__(self, db_type="sqlite", db_path="./honeypot.db"):
        """Initialize validator"""
        self.db_type = db_type
        self.db_path = db_path
        self.db_manager = None
    
    def initialize(self):
        """Initialize database connection"""
        try:
            init_db(db_type=self.db_type, db_path=self.db_path)
            self.db_manager = get_db_manager()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
        return True
    
    def validate(self) -> dict:
        """Validate captured data"""
        try:
            with self.db_manager.get_db_session() as session:
                results = {
                    "total_events": 0,
                    "by_protocol": {},
                    "total_credentials": 0,
                    "total_http_requests": 0,
                    "total_sessions": 0,
                    "top_attackers": [],
                    "top_usernames": [],
                    "sample_events": []
                }
                
                # Count total events by protocol
                events = session.query(AttackEvent).all()
                results["total_events"] = len(events)
                
                protocol_counts = session.query(
                    AttackEvent.protocol,
                    func.count(AttackEvent.id)
                ).group_by(AttackEvent.protocol).all()
                
                for protocol, count in protocol_counts:
                    results["by_protocol"][protocol] = count
                
                # Count credentials
                credentials = session.query(Credential).all()
                results["total_credentials"] = len(credentials)
                
                # Count HTTP requests
                http_requests = session.query(HTTPRequest).all()
                results["total_http_requests"] = len(http_requests)
                
                # Count sessions
                sessions = session.query(Session).all()
                results["total_sessions"] = len(sessions)
                
                # Top attackers (by IP)
                top_ips = session.query(
                    AttackEvent.ip,
                    func.count(AttackEvent.id).label("count")
                ).group_by(AttackEvent.ip).order_by(func.count(AttackEvent.id).desc()).limit(10).all()
                
                results["top_attackers"] = [{"ip": ip, "count": count} for ip, count in top_ips]
                
                # Top attempted usernames
                top_users = session.query(
                    Credential.username,
                    func.count(Credential.id).label("count")
                ).group_by(Credential.username).order_by(func.count(Credential.id).desc()).limit(10).all()
                
                results["top_usernames"] = [{"username": user, "count": count} for user, count in top_users]
                
                # Sample recent events
                recent_events = session.query(AttackEvent).order_by(AttackEvent.timestamp.desc()).limit(10).all()
                
                for event in recent_events:
                    results["sample_events"].append({
                        "id": event.id,
                        "ip": event.ip,
                        "protocol": event.protocol,
                        "timestamp": str(event.timestamp),
                        "success": event.success
                    })
                
                return results
        
        except Exception as e:
            logger.error(f"Error validating database: {e}")
            return None
    
    def print_report(self, results: dict):
        """Print validation report"""
        if not results:
            logger.error("No results to print")
            return
        
        print("\n" + "="*60)
        print("HONEYPOT DATA VALIDATION REPORT")
        print("="*60)
        
        print(f"\nTotal Events Captured: {results['total_events']}")
        
        print("\nEvents by Protocol:")
        for protocol, count in results['by_protocol'].items():
            print(f"  {protocol}: {count}")
        
        print(f"\nTotal Credentials Attempted: {results['total_credentials']}")
        print(f"Total HTTP Requests: {results['total_http_requests']}")
        print(f"Total Sessions: {results['total_sessions']}")
        
        print("\nTop 10 Attacker IPs:")
        for idx, attacker in enumerate(results['top_attackers'], 1):
            print(f"  {idx}. {attacker['ip']}: {attacker['count']} attempts")
        
        print("\nTop 10 Attempted Usernames:")
        for idx, user in enumerate(results['top_usernames'], 1):
            print(f"  {idx}. {user['username']}: {user['count']} attempts")
        
        print("\nRecent 10 Events:")
        for idx, event in enumerate(results['sample_events'], 1):
            print(f"  {idx}. [{event['protocol']}] {event['ip']} @ {event['timestamp']}")
        
        print("\n" + "="*60)
        
        # Validation checks
        print("\nVALIDATION CHECKS:")
        
        if results['total_events'] == 0:
            print("  ⚠️  WARNING: No events captured!")
        else:
            print(f"  ✓ Events captured: {results['total_events']}")
        
        if results['total_credentials'] == 0:
            print("  ⚠️  WARNING: No credentials captured!")
        else:
            print(f"  ✓ Credentials captured: {results['total_credentials']}")
        
        if results['total_http_requests'] == 0:
            print("  ⚠️  WARNING: No HTTP requests captured!")
        else:
            print(f"  ✓ HTTP requests captured: {results['total_http_requests']}")
        
        if results['total_sessions'] == 0:
            print("  ⚠️  WARNING: No sessions recorded!")
        else:
            print(f"  ✓ Sessions recorded: {results['total_sessions']}")
        
        print("\n" + "="*60 + "\n")


def main():
    """Run database validation"""
    validator = DatabaseValidator(db_type="sqlite", db_path="./honeypot.db")
    
    if not validator.initialize():
        logger.error("Failed to initialize database validator")
        sys.exit(1)
    
    results = validator.validate()
    validator.print_report(results)


if __name__ == "__main__":
    main()
