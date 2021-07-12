import asyncio
from ocpp.v201 import call
import aiohttp.web
from aiohttp import web
from ocpp.v201.enums import AuthorizationStatusType


class ChargerApi:
    def __init__(self, cp, port: int = 8080):
        self.cp = cp
        self.port = port

    async def authorize_rfid(self, request):
        payload = await request.json()

        result = await self.cp.call(call.AuthorizePayload(
            id_token=payload
        ))
        return web.json_response(
            data={},
            status=200 if result.id_token_info['status'] == AuthorizationStatusType.accepted else 400
        )

    async def start(self):
        app = web.Application()
        app.router.add_post('/authorize_rfid', self.authorize_rfid)

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()

        site = aiohttp.web.TCPSite(
            runner=runner,
            port=self.port,
            host='0.0.0.0'
        )
        await site.start()

        while True:
            await asyncio.sleep(3600)
