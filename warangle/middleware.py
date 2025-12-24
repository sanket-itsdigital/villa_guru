
import logging
import json

logger = logging.getLogger("django.request")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Basic log (same as before)
        logger.info(f"{request.method} {request.get_full_path()} - {response.status_code}")

        # Log more detail for 4xx and 5xx responses
        if response.status_code >= 400:
            try:
                # Try to decode response JSON if possible
                content = response.content.decode("utf-8")
                body = json.loads(content) if content else {}
            except Exception:
                body = response.content.decode(errors="ignore")

            user_info = request.user if getattr(request, "user", None) and request.user.is_authenticated else "Anonymous"

            logger.warning(
                f"⚠️ {request.method} {request.get_full_path()} "
                f"returned {response.status_code} for {user_info}. "
                f"Response body: {body}"
            )

        return response
