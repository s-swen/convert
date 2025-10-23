# ==========================================================
# ✉️ Email Notification Service (with Production Logging)
# ==========================================================

import json
import smtplib
import os
import logging
from email.message import EmailMessage


# 🪵 Logger setup (universal: works in dev + prod)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
)
logger = logging.getLogger(__name__)


def notification(message):
    """
    Sends an email alert when an MP3 file is not ready.
    Returns None if successful, or Exception if failed.
    """

    try:
        # 🧩 Step 1: Parse message safely
        logger.debug(f"📦 Raw message received: {message}")
        message = json.loads(message)
        mp3_fid = message.get('mp3_fid')
        if not mp3_fid:
            raise ValueError("Missing required key 'mp3_fid' in message.")
        logger.info(f"🎵 Processing MP3 file_id: {mp3_fid}")

        # 🧠 Step 2: Load environment variables
        sender_address = os.environ.get('GMAIL_ADDRESS')
        sender_password = os.environ.get('GMAIL_PASSWORD')
        receiver_address = 'zoeharris168@gmail.com'

        if not sender_address or not sender_password:
            raise EnvironmentError("❌ Gmail credentials not set in environment variables.")
        logger.debug(f"📧 Sender: {sender_address}, Receiver: {receiver_address}")

        # 💌 Step 3: Create email message
        msg = EmailMessage()
        msg.set_content(f"⚠️ MP3 file_id `{mp3_fid}` is now ready!")
        msg['Subject'] = "MP3 Download Notification"
        msg['From'] = sender_address
        msg['To'] = receiver_address
        logger.debug("🧱 Email message object created successfully.")

        # 🚀 Step 4: Send via Gmail SMTP
        logger.info("🔗 Connecting to Gmail SMTP server...")
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=5) as session:
            session.starttls()
            logger.info("🔒 TLS connection established.")
            session.login(sender_address, sender_password)
            logger.info("✅ Logged in to Gmail successfully.")
            session.send_message(msg)
            logger.info(f"📤 Email sent to {receiver_address} for file_id: {mp3_fid}")

        return None  # ✅ No errors

    except json.JSONDecodeError as e:
        logger.exception("🧨 Failed to parse incoming JSON message.")
        return e

    except smtplib.SMTPAuthenticationError as e:
        logger.exception("🔑 Gmail authentication failed. Check credentials.")
        return e

    except smtplib.SMTPException as e:
        logger.exception("📡 SMTP error occurred while sending email.")
        return e

    except Exception as e:
        logger.exception("🔥 Unexpected error occurred during email notification.")
        return e
