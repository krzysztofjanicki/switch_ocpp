import asyncio
import logging
import websockets
from datetime import datetime
import base64
from typing import Optional
from ocpp.routing import on
from ocpp.v201 import ChargePoint as CoreChargePoint
from ocpp.v201 import call_result
from ocpp.v201.enums import AuthorizationStatusType, IdTokenType, RegistrationStatusType, Action
from model.ChargerPointCfg import ChargerPointCfg as cfg
from central_system_state import CentralSystemState
from ocpp.exceptions import GenericError

logging.basicConfig(level=logging.INFO)

state: Optional[CentralSystemState] = None


class ChargePoint(CoreChargePoint):

    @on(Action.BootNotification)
    async def on_boot_notification(self, charging_station: dict, reason: str, **kwargs) \
            -> call_result.BootNotificationPayload:
        if not state.validate_change_state(self.id, Action.BootNotification):
            raise GenericError(details=Action.BootNotification + ' not allowed in this state')

        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatusType.accepted
        )

    @on(Action.StatusNotification)
    async def on_status_notification(self, timestamp: str, connector_status: str, evse_id: int, connector_id: int, **kwargs)\
            -> call_result.StatusNotificationPayload:
        if not state.validate_change_state(self.id, Action.StatusNotification):
            raise GenericError(details=Action.StatusNotification + ' not allowed in this state')
        return call_result.StatusNotificationPayload()

    @on(Action.Authorize)
    async def on_authorize(self, id_token: dict, **kwargs) -> call_result.AuthorizePayload:

        status = AuthorizationStatusType.accepted
        try:
            result = bytearray.fromhex(id_token['id_token'])
            if len(result) not in [4, 7] or id_token['type'] != IdTokenType.iso14443:
                status = AuthorizationStatusType.invalid
        finally:
            status = AuthorizationStatusType.invalid

        return call_result.AuthorizePayload(
            id_token_info={'status': status}
        )


def validate_user_header(request_header: str) -> bool:
    return request_header == 'Basic ' + base64.b64encode(f'{cfg.user}:{cfg.password}'.encode('utf-8')).decode('utf-8')


async def on_connect(websocket, path):

    global state
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. "
                     "Closing Connection")
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    if 'Authorization' not in websocket.request_headers \
            or not validate_user_header(request_header=websocket.request_headers['Authorization']):
        logging.error('Authorization header invalid')
        return await websocket.close()
    state = CentralSystemState()
    charge_point_id = path.strip('/')

    cp = ChargePoint(charge_point_id, websocket)
    state.add_handled_charging_point(charge_point_id)
    await cp.start()


async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp2.0.1']
    )
    logging.info("WS Server Ready")
    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
