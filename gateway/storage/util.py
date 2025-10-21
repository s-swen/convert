import pika, json, logging

# 🪶 UPDATED LOGGING
logger = logging.getLogger(__name__)

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
        logger.info(f"💾 File stored in GridFS with id: {fid}")
    except Exception as err:
        logger.exception("🔥 Failed to save file to GridFS")
        return 'internal server error', 500

    message = {
        'video_fid': str(fid),
        'mp3_fid': None,
        'username': access['username']
    }

    try:
        channel.basic_publish(
            exchange='',
            routing_key='video',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        logger.info(f"📨 Message sent to RabbitMQ for user: {access['username']}")
    except Exception as e:
        fs.delete(fid)
        logger.exception("🔥 Failed to publish message to RabbitMQ, file deleted.")
        return 'internal server error', 500
