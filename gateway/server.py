# 🪶 UPDATED LOGGING
import os, gridfs, pika, json, logging, time
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

# 🪶 UPDATED LOGGING CONFIG
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "WARNING"),
    format="%(asctime)s [%(levelname)s] ⚙️ %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------
# 🌸 Flask setup
# ---------------------------------------------
server = Flask(__name__)
server.config['MONGO_URI'] = "mongodb://root:rootpassword@mongodb-0.mongodb:27017/videos?authSource=admin"

# ---------------------------------------------
# 🍃 MongoDB connection (same)
# ---------------------------------------------
try:
    mongo = PyMongo(server)
    fs = gridfs.GridFS(mongo.db)
    logger.info("🍃 MongoDB connection established successfully.")
except Exception as e:
    logger.exception("🔥 MongoDB connection failed!")
    mongo = None
    fs = None

# ==========================================================
# 🪶 UPDATED: Infinite retry loop for RabbitMQ connection 🐇
# ==========================================================
def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            channel = connection.channel()
            logger.info("✅ 🐇 Successfully connected to RabbitMQ.")
            return connection, channel
        except Exception as e:
            logger.warning(f"⚠️  RabbitMQ not ready yet: {e}")
            time.sleep(5)  # Wait before retrying

connection, channel = connect_to_rabbitmq()
# ==========================================================

# ---------------------------------------------
# 🔐 Login route
# ---------------------------------------------
@server.route('/login', methods=['POST'])
def login():
    try:
        token, err = access.login(request)
        if not err:
            logger.info("🔑 Login successful.")
            return token
        else:
            logger.warning(f"❌ Login failed: {err}")
            return err
    except Exception as e:
        logger.exception("🔥 Unexpected error during /login")
        return "internal server error", 500

# ---------------------------------------------
# 📤 Upload route
# ---------------------------------------------
@server.route('/upload', methods=['POST'])
def upload():
    try:
        decoded, err = validate.token(request)
        if err:
            logger.warning(f"🚫 Token validation failed: {err}")
            return err

        decoded = json.loads(decoded)

        if decoded['admin']:
            if len(request.files) != 1:
                logger.warning("⚠️ Upload failed: expected exactly 1 file.")
                return 'exactly 1 file required', 400

            for _, f in request.files.items():
                err = util.upload(f, fs, channel, decoded)
                if err:
                    logger.error(f"💥 Upload error: {err}")
                    return err

            logger.info("📤 Upload successful.")
            return 'success', 200

        else:
            logger.warning("⛔ Unauthorized upload attempt.")
            return 'not authorized', 401

    except Exception as e:
        logger.exception("🔥 Unexpected error during /upload")
        return 'internal server error', 500

# ---------------------------------------------
# ⬇️ Download route (placeholder)
# ---------------------------------------------
@server.route('/download', methods=['GET'])
def download():
    pass

# ---------------------------------------------
# 🚀 Run server
# ---------------------------------------------
if __name__ == '__main__':
    logger.info("🚀 Starting Flask server...")
    server.run(host='0.0.0.0', port=8080)
