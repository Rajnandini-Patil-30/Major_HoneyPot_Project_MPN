"""
HoneyShield Demo Attack Simulator
Dual-mode: protocol-level attacks + geo-diverse database seeding.

Usage:
    python demo_attack_simulator.py --target localhost
    python demo_attack_simulator.py --target localhost --seed-geo
    python demo_attack_simulator.py --seed-geo-only
"""

import argparse
import socket
import time
import random
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ============================================================
# Pre-looked-up geo data for 30 real-world IPs from diverse countries
# These get seeded directly into the database for map diversity
# ============================================================
GEO_SEED_DATA = [
    {"ip": "8.8.8.8", "country": "United States", "country_code": "US", "city": "Ashburn", "region": "Virginia", "lat": 39.0438, "lon": -77.4874, "isp": "Google LLC", "asn": "AS15169"},
    {"ip": "1.1.1.1", "country": "Australia", "country_code": "AU", "city": "Sydney", "region": "NSW", "lat": -33.8688, "lon": 151.2093, "isp": "Cloudflare", "asn": "AS13335"},
    {"ip": "9.9.9.9", "country": "United States", "country_code": "US", "city": "Berkeley", "region": "California", "lat": 37.8749, "lon": -122.2586, "isp": "Quad9", "asn": "AS19281"},
    {"ip": "185.220.101.1", "country": "Germany", "country_code": "DE", "city": "Frankfurt", "region": "Hesse", "lat": 50.1109, "lon": 8.6821, "isp": "Tor Exit Node", "asn": "AS205100"},
    {"ip": "45.33.32.156", "country": "United States", "country_code": "US", "city": "Fremont", "region": "California", "lat": 37.5483, "lon": -121.9886, "isp": "Linode", "asn": "AS63949"},
    {"ip": "91.189.88.181", "country": "United Kingdom", "country_code": "GB", "city": "London", "region": "England", "lat": 51.5074, "lon": -0.1278, "isp": "Canonical Ltd", "asn": "AS41231"},
    {"ip": "104.16.132.229", "country": "United States", "country_code": "US", "city": "San Francisco", "region": "California", "lat": 37.7749, "lon": -122.4194, "isp": "Cloudflare", "asn": "AS13335"},
    {"ip": "77.88.55.77", "country": "Russia", "country_code": "RU", "city": "Moscow", "region": "Moscow", "lat": 55.7558, "lon": 37.6173, "isp": "Yandex LLC", "asn": "AS13238"},
    {"ip": "180.76.76.76", "country": "China", "country_code": "CN", "city": "Beijing", "region": "Beijing", "lat": 39.9042, "lon": 116.4074, "isp": "Baidu", "asn": "AS38365"},
    {"ip": "168.63.129.16", "country": "Netherlands", "country_code": "NL", "city": "Amsterdam", "region": "North Holland", "lat": 52.3676, "lon": 4.9041, "isp": "Microsoft Azure", "asn": "AS8075"},
    {"ip": "200.160.2.3", "country": "Brazil", "country_code": "BR", "city": "Sao Paulo", "region": "SP", "lat": -23.5505, "lon": -46.6333, "isp": "NIC.br", "asn": "AS22548"},
    {"ip": "41.63.96.0", "country": "South Africa", "country_code": "ZA", "city": "Johannesburg", "region": "Gauteng", "lat": -26.2041, "lon": 28.0473, "isp": "Microsoft", "asn": "AS8075"},
    {"ip": "103.224.182.250", "country": "India", "country_code": "IN", "city": "Mumbai", "region": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "isp": "Web Werks", "asn": "AS133982"},
    {"ip": "156.154.70.1", "country": "United States", "country_code": "US", "city": "New York", "region": "New York", "lat": 40.7128, "lon": -74.0060, "isp": "Neustar", "asn": "AS7786"},
    {"ip": "193.0.14.129", "country": "Netherlands", "country_code": "NL", "city": "Amsterdam", "region": "North Holland", "lat": 52.3740, "lon": 4.8897, "isp": "RIPE NCC", "asn": "AS25152"},
    {"ip": "202.12.27.33", "country": "Japan", "country_code": "JP", "city": "Tokyo", "region": "Tokyo", "lat": 35.6762, "lon": 139.6503, "isp": "WIDE Project", "asn": "AS2500"},
    {"ip": "199.7.83.42", "country": "United States", "country_code": "US", "city": "Los Angeles", "region": "California", "lat": 34.0522, "lon": -118.2437, "isp": "ICANN", "asn": "AS20144"},
    {"ip": "195.46.39.39", "country": "Ukraine", "country_code": "UA", "city": "Kyiv", "region": "Kyiv", "lat": 50.4501, "lon": 30.5234, "isp": "Safe DNS", "asn": "AS56600"},
    {"ip": "178.22.122.100", "country": "Iran", "country_code": "IR", "city": "Tehran", "region": "Tehran", "lat": 35.6892, "lon": 51.3890, "isp": "Shecan", "asn": "AS58224"},
    {"ip": "101.101.101.101", "country": "Taiwan", "country_code": "TW", "city": "Taipei", "region": "Taipei", "lat": 25.0330, "lon": 121.5654, "isp": "TWNIC", "asn": "AS131596"},
    {"ip": "119.29.29.29", "country": "China", "country_code": "CN", "city": "Shanghai", "region": "Shanghai", "lat": 31.2304, "lon": 121.4737, "isp": "Tencent", "asn": "AS132203"},
    {"ip": "176.103.130.130", "country": "Netherlands", "country_code": "NL", "city": "Rotterdam", "region": "South Holland", "lat": 51.9225, "lon": 4.4792, "isp": "AdGuard", "asn": "AS212772"},
    {"ip": "94.140.14.14", "country": "Cyprus", "country_code": "CY", "city": "Limassol", "region": "Limassol", "lat": 34.6823, "lon": 33.0464, "isp": "AdGuard", "asn": "AS212772"},
    {"ip": "114.114.114.114", "country": "China", "country_code": "CN", "city": "Nanjing", "region": "Jiangsu", "lat": 32.0603, "lon": 118.7969, "isp": "China Unicom", "asn": "AS4837"},
    {"ip": "223.5.5.5", "country": "China", "country_code": "CN", "city": "Hangzhou", "region": "Zhejiang", "lat": 30.2741, "lon": 120.1551, "isp": "Alibaba", "asn": "AS37963"},
    {"ip": "46.101.250.135", "country": "Germany", "country_code": "DE", "city": "Berlin", "region": "Berlin", "lat": 52.5200, "lon": 13.4050, "isp": "DigitalOcean", "asn": "AS14061"},
    {"ip": "159.89.120.99", "country": "Singapore", "country_code": "SG", "city": "Singapore", "region": "Singapore", "lat": 1.3521, "lon": 103.8198, "isp": "DigitalOcean", "asn": "AS14061"},
    {"ip": "139.162.130.30", "country": "Japan", "country_code": "JP", "city": "Osaka", "region": "Osaka", "lat": 34.6937, "lon": 135.5023, "isp": "Linode", "asn": "AS63949"},
    {"ip": "167.99.192.200", "country": "India", "country_code": "IN", "city": "Bangalore", "region": "Karnataka", "lat": 12.9716, "lon": 77.5946, "isp": "DigitalOcean", "asn": "AS14061"},
    {"ip": "188.114.97.1", "country": "France", "country_code": "FR", "city": "Paris", "region": "Ile-de-France", "lat": 48.8566, "lon": 2.3522, "isp": "Cloudflare", "asn": "AS13335"},
]

# Common credential pairs for brute force simulation
CREDENTIALS = [
    ("root", "root"), ("root", "toor"), ("root", "123456"), ("root", "password"),
    ("admin", "admin"), ("admin", "password"), ("admin", "123456"), ("admin", "admin123"),
    ("user", "user"), ("user", "password"), ("ubuntu", "ubuntu"), ("test", "test"),
    ("pi", "raspberry"), ("oracle", "oracle"), ("postgres", "postgres"),
    ("ftpuser", "ftp123"), ("anonymous", "guest@"), ("www-data", "www-data"),
    ("mysql", "mysql"), ("guest", "guest"),
]

PROTOCOLS = ["SSH", "HTTP", "FTP", "Telnet"]


def seed_geo_database():
    """Seed the database with geo-diverse attack records for map visualization."""
    from database.connection import init_db, get_db_manager
    from database.models import AttackEvent, GeoData, Credential, Command
    from datetime import datetime, timedelta

    # Initialize database
    db_type = os.getenv("DB_TYPE", "sqlite")
    if db_type == "sqlite":
        db_path = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), '..', 'honeypot.db'))
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

    db_manager = get_db_manager()
    now = datetime.utcnow()
    events_created = 0

    print(f"\n[*] Seeding database with {len(GEO_SEED_DATA)} geo-diverse attack records...")

    for i, geo in enumerate(GEO_SEED_DATA):
        with db_manager.get_db_session() as session:
            # Check if GeoData already exists for this IP
            existing_geo = session.query(GeoData).filter_by(ip=geo["ip"]).first()

            # Create 2-8 attack events per IP, spread over last 24 hours
            num_events = random.randint(2, 8)
            protocol = random.choice(PROTOCOLS)

            for j in range(num_events):
                time_offset = timedelta(
                    hours=random.uniform(0, 24),
                    minutes=random.randint(0, 59)
                )
                event = AttackEvent(
                    timestamp=now - time_offset,
                    ip=geo["ip"],
                    protocol=protocol,
                    port={"SSH": 2222, "HTTP": 8080, "FTP": 2121, "Telnet": 2323}[protocol],
                    success=False,
                )
                session.add(event)
                session.flush()

                # Add credential for SSH/FTP/Telnet
                if protocol in ("SSH", "FTP", "Telnet"):
                    username, password = random.choice(CREDENTIALS)
                    cred = Credential(
                        event_id=event.id,
                        username=username,
                        password=password,
                        timestamp=event.timestamp,
                    )
                    session.add(cred)

                # Add commands for some SSH events
                if protocol == "SSH" and j == 0:
                    commands = ["whoami", "uname -a", "cat /etc/passwd", "ls -la /"]
                    for cmd_str in commands:
                        cmd = Command(
                            event_id=event.id,
                            command=cmd_str,
                            output="(simulated output)",
                            timestamp=event.timestamp,
                        )
                        session.add(cmd)

                events_created += 1

                # Create GeoData if not exists
                if not existing_geo and j == 0:
                    geo_entry = GeoData(
                        event_id=event.id,
                        ip=geo["ip"],
                        country=geo["country"],
                        country_code=geo["country_code"],
                        city=geo["city"],
                        region=geo["region"],
                        latitude=geo["lat"],
                        longitude=geo["lon"],
                        timezone="UTC",
                        isp=geo["isp"],
                        asn=geo["asn"],
                        cached_at=now,
                    )
                    session.add(geo_entry)

            session.commit()

        # Progress feedback
        progress = (i + 1) / len(GEO_SEED_DATA) * 100
        print(f"  [{progress:5.1f}%] Seeded {geo['city']}, {geo['country']} ({geo['ip']})")

    print(f"\n[+] Done! Created {events_created} attack events from {len(GEO_SEED_DATA)} countries.")
    print(f"[+] The world map should now show pins across the globe.")


def attack_ssh(target, port=2222):
    """Send SSH brute force attempts."""
    print(f"\n[*] SSH brute force against {target}:{port}")
    for username, password in random.sample(CREDENTIALS, min(5, len(CREDENTIALS))):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((target, port))
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            print(f"  Banner: {banner.strip()}")
            sock.close()
            print(f"  Tried: {username}:{password}")
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"  Error: {e}")
            break


def attack_http(target, port=8080):
    """Send HTTP attack probes."""
    paths = [
        "GET / HTTP/1.1",
        "GET /admin HTTP/1.1",
        "GET /../../etc/passwd HTTP/1.1",
        "GET /wp-login.php HTTP/1.1",
        "POST /login HTTP/1.1",
    ]
    print(f"\n[*] HTTP scanning against {target}:{port}")
    for req in paths:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((target, port))
            sock.send(f"{req}\r\nHost: {target}\r\nUser-Agent: Mozilla/5.0\r\n\r\n".encode())
            resp = sock.recv(1024).decode('utf-8', errors='ignore')
            print(f"  {req.split()[1]} -> {resp[:60]}...")
            sock.close()
            time.sleep(random.uniform(0.5, 2))
        except Exception as e:
            print(f"  Error: {e}")
            break


def attack_ftp(target, port=2121):
    """Send FTP login attempts."""
    print(f"\n[*] FTP brute force against {target}:{port}")
    for username, password in random.sample(CREDENTIALS, min(4, len(CREDENTIALS))):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((target, port))
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.send(f"USER {username}\r\n".encode())
            sock.recv(1024)
            sock.send(f"PASS {password}\r\n".encode())
            resp = sock.recv(1024).decode('utf-8', errors='ignore')
            print(f"  {username}:{password} -> {resp.strip()}")
            sock.send(b"QUIT\r\n")
            sock.close()
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"  Error: {e}")
            break


def attack_telnet(target, port=2323):
    """Send Telnet login attempts."""
    print(f"\n[*] Telnet brute force against {target}:{port}")
    for username, password in random.sample(CREDENTIALS, min(3, len(CREDENTIALS))):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((target, port))
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.send(f"{username}\r\n".encode())
            time.sleep(0.5)
            sock.recv(1024)
            sock.send(f"{password}\r\n".encode())
            time.sleep(0.5)
            resp = sock.recv(1024).decode('utf-8', errors='ignore')
            print(f"  {username}:{password} -> {resp.strip()[:60]}")
            sock.close()
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"  Error: {e}")
            break


def main():
    parser = argparse.ArgumentParser(description="HoneyShield Demo Attack Simulator")
    parser.add_argument("--target", default="localhost", help="Target host")
    parser.add_argument("--seed-geo", action="store_true", help="Also seed geo-diverse data into DB")
    parser.add_argument("--seed-geo-only", action="store_true", help="Only seed geo data, no protocol attacks")
    args = parser.parse_args()

    print("=" * 60)
    print("  HONEYSHIELD DEMO ATTACK SIMULATOR")
    print("=" * 60)

    # Seed geo data if requested
    if args.seed_geo or args.seed_geo_only:
        seed_geo_database()

    if args.seed_geo_only:
        print("\n[*] Geo seeding complete. Skipping protocol attacks.")
        return

    # Run protocol-level attacks
    print(f"\n[*] Running protocol attacks against {args.target}...")
    print(f"[*] These prove the honeypot captures real attack data.")

    attack_ssh(args.target)
    attack_http(args.target)
    attack_ftp(args.target)
    attack_telnet(args.target)

    print("\n" + "=" * 60)
    print("  SIMULATION COMPLETE")
    print("=" * 60)
    print("\n[+] Check the dashboard to see captured events and map pins.")


if __name__ == "__main__":
    main()
