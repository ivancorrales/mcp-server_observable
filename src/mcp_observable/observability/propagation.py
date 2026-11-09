from opentelemetry import context, propagate


class TraceContextMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        headers = {
            key.decode().lower(): value.decode()
            for key, value in scope["headers"]
        }

        token = context.attach(
            propagate.extract(carrier=headers)
        )

        try:
            await self.app(scope, receive, send)

        finally:
            context.detach(token)