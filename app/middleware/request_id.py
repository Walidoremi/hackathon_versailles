import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, header_name: str = "x-request-id"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request, call_next):
        rid = request.headers.get(self.header_name, str(uuid.uuid4()))
        request.state.request_id = rid
        response = await call_next(request)
        response.headers[self.header_name] = rid
        return response
