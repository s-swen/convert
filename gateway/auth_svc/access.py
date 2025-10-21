import os, requests, logging

# 🪶 UPDATED LOGGING
logger = logging.getLogger(__name__)

def login(request):
    auth = request.authorization
    if not auth:
        logger.warning("🚫 Missing credentials in login request.")
        return None, ('missing credentials', 401)

    try:
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
            auth=(auth.username, auth.password)
        )
        if response.status_code == 200:
            logger.info("🔑 User logged in successfully.")
            return response.text, None
        else:
            logger.warning(f"❌ Login failed: {response.text}")
            return None, (response.text, response.status_code)
    except Exception as e:
        logger.exception("🔥 Error during login request")
        return None, ('internal server error', 500)
