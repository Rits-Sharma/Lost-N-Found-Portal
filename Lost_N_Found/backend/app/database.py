from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# --------------------------------------------------
# 1. Create MySQL connection URL WITHOUT database
# --------------------------------------------------

SERVER_URL = URL.create(
    drivername="mysql+mysqlconnector",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
)


# --------------------------------------------------
# 2. Connect to MySQL server
# --------------------------------------------------

server_engine = create_engine(
    SERVER_URL,
    echo=True,
    pool_pre_ping=True
)


# --------------------------------------------------
# 3. Create database if it doesn't exist
# --------------------------------------------------

with server_engine.connect() as connection:
    connection.execute(
        text(
            f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}`"
        )
    )


# --------------------------------------------------
# 4. Create URL including database
# --------------------------------------------------

DATABASE_URL = URL.create(
    drivername="mysql+mysqlconnector",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)


# --------------------------------------------------
# 5. Connect to the application database
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)


# --------------------------------------------------
# 6. SQLAlchemy base
# --------------------------------------------------

Base = declarative_base()


# --------------------------------------------------
# 7. Database session
# --------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# --------------------------------------------------
# 8. Database dependency
# --------------------------------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()