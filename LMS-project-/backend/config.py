import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from datetime import timedelta

JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


required_variables = [
    "SECRET_KEY",
    "JWT_SECRET_KEY",
    "DB_HOST",
    "DB_PORT",
    "DB_USERNAME",
    "DB_NAME",
]

missing_variables = [
    variable
    for variable in required_variables
    if not os.getenv(variable)
]

if missing_variables:
    raise RuntimeError(
        "Missing environment variables: "
        + ", ".join(missing_variables)
    )


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:"
        f"{DB_PASSWORD_ENCODED}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")