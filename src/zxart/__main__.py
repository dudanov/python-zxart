import asyncio
import logging

from .client import ZXArtClient
from .common import Entity, Language, Order

logging.basicConfig(level=logging.DEBUG)


async def main():
    async with ZXArtClient(language=Language.RUSSIAN, limit=10) as cli:
        result = await cli.api(
            Entity.TUNE,
            order=Order.MOST_RECENT,
            min_party_place=1,
            years=range(2023, 2026),
        )

        for x in result.result:
            print(x)


asyncio.run(main())
