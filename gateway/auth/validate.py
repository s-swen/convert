import os, requests, logging

# 🪶 UPDATED LOGGING
logger = logging.getLogger(__name__)

def token(request):
    if not 'Authorization' in request.headers:
        logger.warning("🚫 Missing Authorization header.")
        return None, ('missing credentials', 401)

    token = request.headers['Authorization']
    if not token:
        logger.warning("🚫 Empty token provided.")
        return None, ('missing credentials', 401)

    try:
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
            headers={'Authorization': token}
        )
        if response.status_code == 200:
            logger.info("✅ Token validated successfully.")
            return response.text, None
        else:
            logger.warning(f"❌ Token validation failed: {response.text}")
            return None, (response.text, response.status_code)
    except Exception as e:
        logger.exception("🔥 Error during token validation")
        return None, ('internal server error', 500)
