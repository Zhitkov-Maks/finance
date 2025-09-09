from dataclasses import dataclass
from typing import Tuple
import aiohttp


@dataclass
class Client:
    """A class for server requests to reduce repetitive code.

    This class provides asynchronous HTTP methods for making requests
    to a server with standardized timeout and headers configuration.

    :param url: The URL endpoint for the HTTP requests
    :type url: str
    :param data: Optional data payload for POST, PATCH, and PUT requests
    :type data: dict | None
    """

    url: str
    data: dict | None = None
    header = {"Content-Type": "application/json"}

    async def post(self) -> Tuple[int, dict]:
        """Make an asynchronous POST request to the server.

        :return: Tuple containing HTTP status code and response data
        :rtype: Tuple[int, dict]
        :raises: aiohttp.ClientError if the request fails
        """
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(60)
        ) as client:
            async with client.post(
                url=self.url, json=self.data, headers=self.header
            ) as response:
                if response.status == 204:
                    data = {}
                else:
                    data: dict = await response.json()
                return response.status, data

    async def get(self) -> Tuple[int, dict]:
        """Make an asynchronous GET request to the server.

        :return: Tuple containing HTTP status code and response data
        :rtype: Tuple[int, dict]
        :raises: aiohttp.ClientError if the request fails
        """
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(60)
        ) as client:
            async with client.get(
                    url=self.url, headers=self.header
            ) as response:
                data: dict = await response.json()
                return response.status, data

    async def delete(self) -> Tuple[int, dict]:
        """Make an asynchronous DELETE request to the server.

        :return: Tuple containing HTTP status code and response data
        :rtype: Tuple[int, dict]
        :raises: aiohttp.ClientError if the request fails
        """
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(60)
        ) as client:
            async with client.delete(
                    url=self.url, headers=self.header
            ) as response:
                if response.status != 204:
                    return response.status, await response.json()
                return response.status, {"result": True}

    async def patch(self) -> Tuple[int, dict]:
        """Make an asynchronous PATCH request to the server.

        :return: Tuple containing HTTP status code and response data
        :rtype: Tuple[int, dict]
        :raises: aiohttp.ClientError if the request fails
        """
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(60)
        ) as client:
            async with client.patch(
                url=self.url, json=self.data, headers=self.header
            ) as response:
                data: dict = await response.json()
                return response.status, data

    async def put(self) -> Tuple[int, dict]:
        """Make an asynchronous PUT request to the server.

        :return: Tuple containing HTTP status code and response data
        :rtype: Tuple[int, dict]
        :raises: aiohttp.ClientError if the request fails
        """
        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(60)
        ) as client:
            async with client.put(
                url=self.url, json=self.data, headers=self.header
            ) as response:
                data: dict = await response.json()
                return response.status, data
