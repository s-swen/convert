import pika, json, tempfile, os, logging
from bson.objectid import ObjectId
from moviepy import VideoFileClip


# 🪵 Basic logger setup (minimal but production-safe)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def start(message, fs_videos, fs_mp3s, channel):
    try:
        message = json.loads(message)
        logger.info(f"🎬 Processing video_fid={message['video_fid']} for user={message.get('username')}")

        # 🎞️ Read video from GridFS
        tf = tempfile.NamedTemporaryFile()
        out = fs_videos.get(ObjectId(message['video_fid']))
        tf.write(out.read())
        logger.info("✅ Video retrieved from GridFS")

        # 🎧 Extract audio and save temp file
        audio = VideoFileClip(tf.name).audio
        tf.close()
        tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
        audio.write_audiofile(tf_path)
        logger.info(f"🎵 Audio extracted and saved to {tf_path}")

        # 💾 Store MP3 back to Mongo
        with open(tf_path, 'rb') as f:
            data = f.read()
            fid = fs_mp3s.put(data)
        os.remove(tf_path)
        logger.info(f"📦 MP3 uploaded to GridFS with fid={fid}")

        # 🔄 Update message with mp3_fid
        message['mp3_fid'] = str(fid)

        # 📨 Publish result to MP3 queue
        try:
            channel.basic_publish(
                exchange='',
                routing_key=os.environ.get('MP3_QUEUE'),
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            logger.info("✅ Message published to MP3_QUEUE successfully")
        except Exception as err:
            fs_mp3s.delete(fid)
            logger.error(f"❌ Failed to publish message: {err}")
            return 'failed to publish message'

    except Exception as e:
        logger.exception(f"🔥 Unexpected error in conversion: {e}")
        return 'internal server error'
