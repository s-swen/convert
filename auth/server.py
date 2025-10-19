import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL
import logging  # ✅ added for minimal logging

server = Flask(__name__)
mysql = MySQL(server)

# -----------------------------
# CONFIG
# -----------------------------
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

# -----------------------------
# LOGGING CONFIG ✅
# -----------------------------
# Only show warnings and errors by default
logging.basicConfig(
    level=logging.WARNING,  # ⚠️ change to DEBUG for verbose during dev
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# -----------------------------
# ROUTES
# -----------------------------
@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        logging.warning("Login attempt with missing credentials 🚨")  # ✅ minimal logging
        return "missing credentials", 401

    try:
        cur = mysql.connection.cursor()
        res = cur.execute(
            "SELECT email, password FROM user WHERE email=%s", (auth.username,)
        )
        if res > 0:
            user_row = cur.fetchone()
            email, password = user_row

            if auth.username != email or auth.password != password:
                logging.warning(f"Invalid credentials for user {auth.username} 🔑")  # ✅ minimal logging
                return "invalid credentials", 401
            else:
                return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
        else:
            logging.warning(f"Login failed, user not found: {auth.username} 👤")  # ✅ minimal logging
            return "invalid credentials", 401

    except Exception as e:
        logging.error(f"Database error during login: {e} ❌")  # ✅ critical error logging
        return "internal server error", 500


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        logging.warning("Validation attempt with missing token 🚫")  # ✅ minimal logging
        return "missing credentials", 401

    try:
        encoded_jwt = encoded_jwt.split(" ")[1]
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except Exception as e:
        logging.warning(f"JWT validation failed: {e} 🔓")  # ✅ minimal logging
        return "not authorized", 403

    return decoded, 200


# -----------------------------
# JWT CREATION
# -----------------------------
def createJWT(username, secret, authz):
    try:
        return jwt.encode(
            {
                "username": username,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(days=1),
                "iat": datetime.datetime.now(tz=datetime.timezone.utc),
                "admin": authz,
            },
            secret,
            algorithm="HS256",
        )
    except Exception as e:
        logging.error(f"JWT creation failed for {username}: {e} ❌")  # ✅ minimal logging
        return None


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
