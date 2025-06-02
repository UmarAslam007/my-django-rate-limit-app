import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('ip_logs.log')  # log to file
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class LogIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"IP: {ip}")
        return self.get_response(request)
