import os
from dotenv import load_dotenv

# Always reload .env so changes are picked up without restart
load_dotenv(override=True)


def get_db_config():
    """Return DB connection config, reading from .env each call."""
    load_dotenv(override=True)
    return {
        "host":         os.getenv("DB_HOST",     "localhost"),
        "port":         int(os.getenv("DB_PORT", 3306)),
        "user":         os.getenv("DB_USER",     "root"),
        "password":     os.getenv("DB_PASSWORD", ""),
        "database":     os.getenv("DB_NAME",     "Agro"),
        "ssl_disabled": False,   # Required for TiDB Cloud
    }
