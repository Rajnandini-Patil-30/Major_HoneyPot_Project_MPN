"""Seed a handful of public-IP attack events with real geo coordinates
so the dashboard world map has pins to display during the demo."""
import random
from datetime import datetime, timedelta

from database.connection import get_db_manager, init_db
from database.models import AttackEvent, Credential, GeoData, Session as AttackSession

FAKE_ATTACKERS = [
    ("45.227.254.12", "Russia", "RU", "Moscow", 55.7558, 37.6173, "Rostelecom"),
    ("222.186.31.42", "China", "CN", "Shanghai", 31.2304, 121.4737, "ChinaNet"),
    ("185.220.101.7", "Germany", "DE", "Frankfurt", 50.1109, 8.6821, "Tor Exit"),
    ("103.78.12.88", "India", "IN", "Mumbai", 19.0760, 72.8777, "Jio Fiber"),
    ("198.98.51.33", "United States", "US", "Ashburn", 39.0438, -77.4874, "DigitalOcean"),
    ("141.98.10.56", "Netherlands", "NL", "Amsterdam", 52.3676, 4.9041, "M247"),
    ("91.240.118.9", "Ukraine", "UA", "Kyiv", 50.4501, 30.5234, "Datacamp"),
    ("203.0.113.45", "Brazil", "BR", "Sao Paulo", -23.5505, -46.6333, "Telefonica"),
    ("196.196.53.19", "South Africa", "ZA", "Johannesburg", -26.2041, 28.0473, "Liquid"),
    ("114.44.22.199", "Japan", "JP", "Tokyo", 35.6762, 139.6503, "NTT"),
]

PROTOCOLS = ["SSH", "FTP", "Telnet", "HTTP"]
USERS = ["root", "admin", "oracle", "postgres", "pi", "ubuntu", "user", "guest"]
PASSWORDS = ["123456", "password", "admin", "root", "toor", "qwerty", "letmein"]


def seed():
    init_db()
    mgr = get_db_manager()
    with mgr.get_db_session() as db:
        now = datetime.utcnow()
        added = 0
        for ip, country, cc, city, lat, lon, isp in FAKE_ATTACKERS:
            for i in range(random.randint(3, 8)):
                proto = random.choice(PROTOCOLS)
                sess = AttackSession(
                    session_id=f"seed-{ip}-{i}-{random.randint(1000,9999)}",
                    ip=ip,
                    protocol=proto,
                    start_time=now - timedelta(minutes=random.randint(1, 1440)),
                    event_count=1,
                )
                db.add(sess)
                db.flush()

                evt = AttackEvent(
                    timestamp=sess.start_time,
                    ip=ip,
                    protocol=proto,
                    port={"SSH": 2222, "FTP": 2121, "Telnet": 2323, "HTTP": 8080}[proto],
                    source_port=random.randint(30000, 60000),
                    success=False,
                    session_id=sess.id,
                )
                db.add(evt)
                db.flush()

                if proto in ("SSH", "FTP", "Telnet"):
                    db.add(Credential(
                        event_id=evt.id,
                        username=random.choice(USERS),
                        password=random.choice(PASSWORDS),
                    ))
                added += 1

            # one GeoData row per IP (unique constraint)
            existing = db.query(GeoData).filter_by(ip=ip).first()
            if not existing:
                db.add(GeoData(
                    ip=ip, country=country, country_code=cc, city=city,
                    latitude=lat, longitude=lon, isp=isp,
                ))
        db.commit()
        print(f"Seeded {added} attack events across {len(FAKE_ATTACKERS)} countries.")


if __name__ == "__main__":
    seed()
