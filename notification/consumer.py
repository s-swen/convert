import pika, sys, os, time, logging
from send import email


# 🪵 Basic Logger Setup (simple + production safe)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    try:
        # 🐇 RabbitMQ connection        
        def connect_to_rabbitmq():
            while True:
                try:
                    connection = pika.BlockingConnection(
                        pika.ConnectionParameters(host='rabbitmq')
                    )
                    channel = connection.channel()
                    logger.info("✅ Connected to RabbitMQ")
                    return connection, channel
                except Exception as e:
                    logger.exception(f"🔥 RabbitMQ connection failed!: {e}")
                    time.sleep(5)
        connection, channel = connect_to_rabbitmq()


        # 🎧 Consume messages
        def callback(ch, method, properties, body):
            logger.info(f"📩 Received message: {body}")
            err = email.notification(body)
            if err:
                ch.basic_nack(delivery_tag=method.delivery_tag)
                logger.warning("⚠️ email failed, message NACKed.")
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("✅ email successful, message ACKed.")

        channel.basic_consume(
            queue=os.environ.get('MP3_QUEUE'),
            on_message_callback=callback
        )

        logger.info("🚀 Waiting for messages. Press CTRL+C to stop.")
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user. Exiting...")
        sys.exit(0)


if __name__ == '__main__':
    main()
