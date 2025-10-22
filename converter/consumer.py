import pika, sys, os, time, gridfs, logging
from pymongo import MongoClient
from convert import to_mp3


# 🪵 Basic Logger Setup (simple + production safe)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    try:
        # 🍃 MongoDB connection
        try:
            client = MongoClient("mongodb://root:rootpassword@mongodb-0.mongodb:27017?authSource=admin")
            db_videos = client.videos
            db_mp3s = client.mp3s
            fs_videos = gridfs.GridFS(db_videos)
            fs_mp3s = gridfs.GridFS(db_mp3s)
            logger.info("✅ Connected to MongoDB")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return

        # 🐇 RabbitMQ connection
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq')
            )
            channel = connection.channel()
            logger.info("✅ Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            return

        # 🎧 Consume messages
        def callback(ch, method, properties, body):
            logger.info(f"📩 Received message: {body}")
            err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
            if err:
                ch.basic_nack(delivery_tag=method.delivery_tag)
                logger.warning("⚠️ Conversion failed, message NACKed.")
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("✅ Conversion successful, message ACKed.")

        channel.basic_consume(
            queue=os.environ.get('VIDEO_QUEUE'),
            on_message_callback=callback
        )

        logger.info("🚀 Waiting for messages. Press CTRL+C to stop.")
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user. Exiting...")
        sys.exit(0)


if __name__ == '__main__':
    main()
