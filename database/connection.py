"""
Database initialization and connection management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from database.models import Base
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and initialization"""
    
    def __init__(self, db_type="sqlite", db_path="./honeypot.db", **kwargs):
        """
        Initialize database manager
        
        Args:
            db_type: "sqlite" or "postgresql"
            db_path: Path for SQLite database
            **kwargs: Additional arguments for PostgreSQL (host, port, database, user, password)
        """
        self.db_type = db_type
        self.db_path = db_path
        self.kwargs = kwargs
        self.engine = None
        self.SessionLocal = None
        
    def get_connection_string(self):
        """Generate database connection string"""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.db_path}"
        elif self.db_type == "postgresql":
            host = self.kwargs.get("host", "localhost")
            port = self.kwargs.get("port", 5432)
            database = self.kwargs.get("database", "honeypot_db")
            user = self.kwargs.get("user", "honeypot_user")
            password = self.kwargs.get("password", "")
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def initialize(self):
        """Initialize database engine and create tables"""
        try:
            connection_string = self.get_connection_string()
            logger.info(f"Initializing database: {connection_string}")
            
            self.engine = create_engine(
                connection_string,
                echo=False,
                pool_size=20,
                max_overflow=40,
                connect_args={"check_same_thread": False} if self.db_type == "sqlite" else {}
            )
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()
    
    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager = None


def init_db(db_type="sqlite", db_path="./honeypot.db", **kwargs):
    """Initialize global database manager"""
    global db_manager
    db_manager = DatabaseManager(db_type=db_type, db_path=db_path, **kwargs)
    db_manager.initialize()
    return db_manager


def get_db_manager():
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db_manager
