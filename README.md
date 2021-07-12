# OCPP Client / Server test communication
**Table of Content**
- [Test job description](#test-job-description)
- [Requirements](#requirements)
- [Files](#files)
- [Usage](#usage)

## Test job description

Scenario based on Open Charge Point Protocol (OCPP) version 2.0.1:

-   Set up a client (the charging station) and a server (the CSMS) using WebSockets
-   Have the client exchange two messages with the CSMS, one is the BootNotificationRequest and -Response, the other one is the StatusNotificationRequest and -Response. You’ll find more information about those two messages [here](https://www.openchargealliance.org/protocols/ocpp-201/) (hint: have a look at part 2 of the OCPP 2.0.1 specification).
-   Use the Call, CallResult, and CallError mechanism to send the two messages (hint: have a look at part 4 of the OCPP 2.0.1 specification)
-   Use basic authentication (no TLS security) for the charging station to authenticate at the CSMS
-   Make sure the integrity of each message received is validated. You can ignore the optional fields of the messages in your implementation. Hint: you can use the JSON schema files that are provided with the specification if you want.
-   Make sure the messages will be received in the right order, or reply with an error
-   Make sure the client won't send a message until it received a CallResult/CallError

Extension: Implement Authorization using RFID.

-   Add a REST API layer to authorize using RFID and ISO14443 to the charging station (CS).
-   CS should send an AuthorizeRequest message to the CSMS, and the CSMS should respond accordingly (hint: have a look at part 2 of the OCPP 2.0.1 specification).
-   If the token is not ISO14443 compliant the API should return a 400 Bad Request."

## Requirements

- **ocpp==0.8.3**
 https://pypi.org/project/ocpp/ 
 Python package implementing the JSON version of 	   the Open Charge Point Protocol (OCPP).
- **websockets==9.1**
https://websockets.readthedocs.io/en/stable/intro.html
- **aiohttp==3.7.4.post0**
https://docs.aiohttp.org/en/stable/ 
Asynchronous HTTP Client/Server for asyncio and Python.
- **pytest=6.2.4**
https://docs.pytest.org/en/6.2.x/ 
Testing framework
- **pytest-asyncio=0.15.1**
https://pypi.org/project/pytest-asyncio/
for testing asyncio code with pytest.

## Files

`centar_system.py` - CSMS server.

`charging_point.py` - Charging point

`central_system_state.py` - State management for central system

`charging_point_api.py` - REST API for Charging point (route `/authorize_rfid`)

`model/ChargerPointCfg.py` - Some test / default data for test run

`test/TestApiCalls` - pytest tests for API calls 

## Usage
1. Please run `central_system.py` to setup CSMS server
2. Please run `charging_point.py` to boot up Charging Point. Charging point will exchange messages with CSMS as decripted in test job description. 
3. Use curl OR just run pytest to test out response from REST API. First test is considered as valid data (expected response `200`), second two send invalid data and response is expected `400`