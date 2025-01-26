from __future__ import annotations

import logging
from typing import TYPE_CHECKING, overload

import aiohttp

from .common import Language, Sorting, url_from_options
from .models import ResponseModel

if TYPE_CHECKING:
    from typing import Any, Literal, Mapping, Unpack

    from .common import CommonOptions, Entity, SortingSettings
    from .models import Author, AuthorAlias, Music, Picture, ProductCategory
    from .music import MusicOptions, PictureOptions

    type JSONAny = Mapping[str, Any]

_LOGGER = logging.getLogger(__name__)

# Опции по-умолчанию
_DEFAULT_SORTING = Sorting.MOST_RECENT
_DEFAULT_LANGUAGE = Language.RUSSIAN
_DEFAULT_LIMIT = 60


class ZXArtClient:
    _cli: aiohttp.ClientSession
    _language: Language
    _limit: int
    _sorting: Sorting | SortingSettings

    def __init__(
        self,
        *,
        language: Language | None = None,
        limit: int | None = None,
        sorting: Sorting | SortingSettings | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._language = language or _DEFAULT_LANGUAGE
        self._limit = limit or _DEFAULT_LIMIT
        self._sorting = sorting or _DEFAULT_SORTING
        self._cli = session or aiohttp.ClientSession()
        self._close_connector = not session

    async def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_value, traceback):
        return self.close()

    async def close(self):
        if self._close_connector:
            await self._cli.close()

    @overload
    async def api(
        self,
        entity: Literal[Entity.AUTHOR],
        **kwargs: Unpack[CommonOptions],
    ) -> list[Author]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.AUTHOR_ALIAS],
        **kwargs: Unpack[CommonOptions],
    ) -> list[AuthorAlias]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.PRODUCT_CATEGORY],
        **kwargs: Unpack[CommonOptions],
    ) -> list[ProductCategory]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.MUSIC],
        **kwargs: Unpack[MusicOptions],
    ) -> list[Music]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.PICTURE],
        **kwargs: Unpack[PictureOptions],
    ) -> list[Picture]: ...

    async def api(self, entity, **kwargs) -> list[Any]:
        kwargs.setdefault("export", entity)
        kwargs.setdefault("language", self._language)
        kwargs.setdefault("limit", self._limit)
        kwargs.setdefault("order", self._sorting)

        url = url_from_options(**kwargs)

        _LOGGER.debug("API request URL: %s", url)

        async with self._cli.get(url) as x:
            raw_data = await x.read()

        response = ResponseModel.from_json(raw_data)

        return getattr(response.result, entity)
