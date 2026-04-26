"""
Geolocation Service for IP Enrichment
Provides IP-to-location mapping for attacker IPs
"""

import logging
import time
import requests
from typing import Optional, Dict
from database.models import GeoData, AttackEvent
from database.connection import get_db_manager
from datetime import datetime

logger = logging.getLogger(__name__)

# Mock geolocation data for testing
MOCK_GEO_DATA = {
    "127.0.0.1": {
        "country": "Reserved (US)",
        "country_code": "US",
        "city": "Local",
        "region": "Local",
        "latitude": 0.0,
        "longitude": 0.0,
        "timezone": "UTC",
        "isp": "Localhost",
        "asn": "AS0"
    },
    "192.168.": {
        "country": "Private Network",
        "country_code": "XX",
        "city": "Private",
        "region": "Private",
        "latitude": 0.0,
        "longitude": 0.0,
        "timezone": "UTC",
        "isp": "Private Network",
        "asn": "AS0"
    },
    "10.": {
        "country": "Private Network",
        "country_code": "XX",
        "city": "Private",
        "region": "Private",
        "latitude": 0.0,
        "longitude": 0.0,
        "timezone": "UTC",
        "isp": "Private Network",
        "asn": "AS0"
    }
}


class GeolocationService:
    """Geolocation enrichment service"""
    
    def __init__(self, api_key: str = None, use_offline: bool = True, offline_db_path: str = None, cache_ttl: int = 86400):
        """
        Initialize geolocation service
        
        Args:
            api_key: API key for ip-api.com (optional)
            use_offline: Use offline GeoLite2 database
            offline_db_path: Path to offline GeoLite2 database
            cache_ttl: Cache TTL in seconds
        """
        self.api_key = api_key
        self.use_offline = use_offline
        self.offline_db_path = offline_db_path
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, Dict] = {}
        
        logger.info("GeolocationService initialized")
    
    def is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/reserved"""
        # Check localhost
        if ip == "127.0.0.1" or ip.startswith("127."):
            return True
        
        # Check private ranges
        private_ranges = ["192.168.", "10.", "172."]
        for prefix in private_ranges:
            if ip.startswith(prefix):
                return True
        
        return False
    
    def lookup_ip(self, ip: str) -> Optional[Dict]:
        """
        Lookup IP geolocation
        
        Args:
            ip: IP address to lookup
        
        Returns:
            Dictionary with geolocation data
        """
        
        # Check cache first
        if ip in self.cache:
            cached_data, timestamp = self.cache[ip]
            age = datetime.utcnow().timestamp() - timestamp
            if age < self.cache_ttl:
                logger.debug(f"GeoIP cache hit: {ip}")
                return cached_data
        
        # Use mock data for private IPs
        if self.is_private_ip(ip):
            logger.debug(f"Private IP address: {ip}")
            data = MOCK_GEO_DATA.get("127.0.0.1").copy()
        else:
            # Query ip-api.com for real geolocation (free tier: 45 req/min)
            data = self._query_ip_api(ip)
        
        # Cache the result
        self.cache[ip] = (data, datetime.utcnow().timestamp())
        
        logger.debug(f"GeoIP lookup: {ip} -> {data['country']}, {data['city']}")
        return data
    
    def _query_ip_api(self, ip: str) -> Dict:
        """
        Query ip-api.com for geolocation data.
        Free tier: 45 requests/minute. Rate limited with 1.5s sleep.
        """
        try:
            # Rate limit: sleep to stay under 45 req/min
            time.sleep(1.5)

            resp = requests.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,country,countryCode,regionName,city,lat,lon,timezone,isp,as"},
                timeout=5
            )
            resp.raise_for_status()
            result = resp.json()

            if result.get("status") == "success":
                return {
                    "country": result.get("country", "Unknown"),
                    "country_code": result.get("countryCode", "XX"),
                    "city": result.get("city", "Unknown"),
                    "region": result.get("regionName", "Unknown"),
                    "latitude": result.get("lat", 0.0),
                    "longitude": result.get("lon", 0.0),
                    "timezone": result.get("timezone", "UTC"),
                    "isp": result.get("isp", "Unknown"),
                    "asn": result.get("as", "Unknown")
                }
            else:
                logger.warning(f"ip-api.com returned failure for {ip}: {result.get('message')}")
        except requests.RequestException as e:
            logger.warning(f"ip-api.com request failed for {ip}: {e}")

        # Fallback: return unknown data
        return {
            "country": "Unknown",
            "country_code": "XX",
            "city": "Unknown",
            "region": "Unknown",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "isp": "Unknown",
            "asn": "Unknown"
        }

    def enrich_attack_event(self, event_id: int, ip: str) -> bool:
        """
        Enrich attack event with geolocation data.
        Uses upsert logic: skips insert if GeoData already exists for this IP.

        Args:
            event_id: Attack event ID
            ip: IP address

        Returns:
            True if successful
        """
        try:
            # Save to database (check-before-insert to avoid UNIQUE constraint violation)
            db_manager = get_db_manager()
            with db_manager.get_db_session() as session:
                existing = session.query(GeoData).filter_by(ip=ip).first()
                if existing:
                    # Update event_id to latest event for this IP
                    existing.event_id = event_id
                    existing.cached_at = datetime.utcnow()
                    session.commit()
                    logger.debug(f"GeoData already exists for {ip}, updated event_id to {event_id}")
                    return True

            # Lookup geo data (only if we don't already have it)
            geo_data = self.lookup_ip(ip)

            if not geo_data:
                logger.warning(f"Failed to lookup geolocation for {ip}")
                return False

            with db_manager.get_db_session() as session:
                geo_entry = GeoData(
                    event_id=event_id,
                    ip=ip,
                    country=geo_data.get("country"),
                    country_code=geo_data.get("country_code"),
                    city=geo_data.get("city"),
                    region=geo_data.get("region"),
                    latitude=geo_data.get("latitude"),
                    longitude=geo_data.get("longitude"),
                    timezone=geo_data.get("timezone"),
                    isp=geo_data.get("isp"),
                    asn=geo_data.get("asn"),
                    cached_at=datetime.utcnow()
                )
                session.add(geo_entry)
                session.commit()

                logger.info(f"Event {event_id} enriched with geolocation: {geo_data.get('country')}, {geo_data.get('city')}")
                return True

        except Exception as e:
            logger.error(f"Error enriching event with geolocation: {e}")
            return False
    
    def get_top_countries(self, limit: int = 10) -> list:
        """Get top attacking countries"""
        try:
            db_manager = get_db_manager()
            with db_manager.get_db_session() as session:
                from sqlalchemy import func
                top_countries = session.query(
                    GeoData.country,
                    func.count(GeoData.id).label("count")
                ).filter(
                    GeoData.country.isnot(None)
                ).group_by(
                    GeoData.country
                ).order_by(
                    func.count(GeoData.id).desc()
                ).limit(limit).all()
                
                return [{"country": country, "count": count} for country, count in top_countries]
        
        except Exception as e:
            logger.error(f"Error getting top countries: {e}")
            return []


# Global geolocation service instance
_geo_service: Optional[GeolocationService] = None


def init_geo_service(api_key: str = None, use_offline: bool = True, offline_db_path: str = None) -> GeolocationService:
    """Initialize global geolocation service"""
    global _geo_service
    _geo_service = GeolocationService(
        api_key=api_key,
        use_offline=use_offline,
        offline_db_path=offline_db_path
    )
    return _geo_service


def get_geo_service() -> GeolocationService:
    """Get global geolocation service instance"""
    global _geo_service
    if _geo_service is None:
        _geo_service = GeolocationService()
    return _geo_service
