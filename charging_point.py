import asyncio
import logging
import websockets
from datetime import datetime
from ocpp.v201 import call
from ocpp.v201 import ChargePoint as CoreChargePoint
from ocpp.v201.enums import BootReasonType, RegistrationStatusType, ConnectorStatusType
from model.ChargerPointCfg import ChargerPointCfg as cfg
from charging_point_api import ChargerApi
import base64

logging.basicConfig(level=logging.INFO)


class ChargePoint(CoreChargePoint):

    async def send_boot_sequence(self):
        boot_notification_response = await self.call(call.BootNotificationPayload(
            charging_station={
                'model': cfg.model,
                'vendor_name': cfg.vendor_name
            },
            reason=BootReasonType.power_up
        ))

        if boot_notification_response.status == RegistrationStatusType.accepted:
            logging.info(self.id + " Booted confirmed.")

            status_notification_response = await self.call(call.StatusNotificationPayload(
                connector_status=ConnectorStatusType.available,
                timestamp=datetime.utcnow().isoformat(),
                evse_id=cfg.evse_id,
                connector_id=cfg.connector_id))

            # there is no payload in StatusNotificationResponse
            if status_notification_response:
                logging.info(self.id + " Status Notification confirmed")


async def start_client():

    async with websockets.connect(
            f'ws://{cfg.cs_websocket_host}:{cfg.cs_websocket_port}/{cfg.name}',
            subprotocols=['ocpp2.0.1'],
            extra_headers={
                'Authorization': 'Basic ' + base64.b64encode(f'{cfg.user}:{cfg.password}'.encode('utf-8')).decode('utf-8')
            }
    ) as ws:
        cp = ChargePoint(cfg.name, ws)

        charger_api_server = ChargerApi(cp=cp)

        await asyncio.gather(cp.start(), cp.send_boot_sequence(), charger_api_server.start())


if __name__ == '__main__':
    asyncio.run(start_client())
