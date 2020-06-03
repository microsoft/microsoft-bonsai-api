"""
Stub web server for unit tests
Copyright 2020 Microsoft
"""

from aiohttp import web


def get_app():
    stub = SimulatorGatewayStub()
    app = web.Application()
    app.router.add_get("/", stub.root)
    return app


def start_app() -> None:
    the_app = get_app()
    web.run_app(app=the_app, host="127.0.0.1", port=9000)


class SimulatorGatewayStub:
    def __init__(self):
        pass

    async def root(self, request):
        return web.json_response({})


if __name__ == "__main__":
    start_app()
