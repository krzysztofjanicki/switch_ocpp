import pytest
import aiohttp
import os
import asyncio


class TestApiCalls:

    @pytest.mark.asyncio
    async def test_correct_api_call(self):
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8080/authorize_rfid', json={'idToken': os.urandom(4).hex(), 'type': 'ISO14443'}) as response:
                body = await response.json()
            assert response.status == 200

    @pytest.mark.asyncio
    async def test_false_token_api_call(self):
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8080/authorize_rfid', json={'idToken': os.urandom(5).hex(), 'type': 'ISO14443'}) as response:
                body = await response.json()
            assert response.status == 400

    @pytest.mark.asyncio
    async def test_false_token_type_api_call(self):
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8080/authorize_rfid', json={'idToken': os.urandom(4).hex(), 'type': 'ISO15693'}) as response:
                body = await response.json()
            assert response.status == 400

