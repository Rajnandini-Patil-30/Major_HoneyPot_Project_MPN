"""Flush all captured attack data. Keeps the schema, deletes all rows.
Safe to run while the honeypot engine + backend are live."""
from database.connection import get_db_manager, init_db
from database.models import (
    AttackEvent, Credential, Command, HTTPRequest, GeoData, Session as AttackSession,
)


def flush():
    init_db()
    mgr = get_db_manager()
    with mgr.get_db_session() as db:
        counts = {}
        for model in (Credential, Command, HTTPRequest, GeoData, AttackEvent, AttackSession):
            counts[model.__tablename__] = db.query(model).delete()
        db.commit()
    print("Flushed:")
    for table, n in counts.items():
        print(f"  {table}: {n} rows")


if __name__ == "__main__":
    flush()
