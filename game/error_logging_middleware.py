import logging
import traceback
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(f"Uncaught exception: {str(exception)}\n{traceback.format_exc()}")
        return HttpResponse("An error occurred", status=500)