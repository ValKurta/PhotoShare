from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException, Request
from time import time
from collections import defaultdict
import logging

# This will store request count for each IP
requests_per_ip = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app, max_requests: int = 10, window_size: int = 60, block_time: int = 60
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_size = window_size
        self.block_time = block_time
        self.blocked_ips = defaultdict(lambda: 0)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()

        if client_ip in self.blocked_ips:
            if current_time - self.blocked_ips[client_ip] < self.block_time:
                logging.warning(
                    f"Rate limit exceeded for {client_ip}, blocking for {self.block_time} seconds"
                )
                raise HTTPException(
                    status_code=429, detail="Rate limit exceeded, try again later."
                )
            else:
                # Unblock IP after block_time has passed
                del self.blocked_ips[client_ip]

        requests_per_ip[client_ip] = [
            req_time
            for req_time in requests_per_ip[client_ip]
            if current_time - req_time < self.window_size
        ]

        if len(requests_per_ip[client_ip]) >= self.max_requests:
            self.blocked_ips[client_ip] = current_time
            logging.warning(
                f"Rate limit exceeded for {client_ip}, blocking for {self.block_time} seconds"
            )
            raise HTTPException(
                status_code=429, detail="Rate limit exceeded, try again later."
            )

        requests_per_ip[client_ip].append(current_time)

        try:
            response = await call_next(request)
        except Exception as e:
            logging.error(f"Error while processing request from {client_ip}: {e}")
            raise
        return response
