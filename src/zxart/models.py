import dataclasses as dc
import datetime as dt
import html
import re
from decimal import Decimal
from typing import Annotated, Any
from urllib.parse import unquote

from mashumaro.config import BaseConfig
from mashumaro.mixins.dict import DataClassDictMixin
from mashumaro.types import Discriminator

from .common import Entity

_RE_DESCRIPTION = re.compile(r"<pre>(.*)</pre>", re.DOTALL)

type HtmlStr = Annotated[str, "HtmlStr"]
"""Строка с экранированными символами HTML"""

type UrlStr = Annotated[str, "UrlStr"]
"""Строка с экранированными символами URL"""


def _unescape(value: str) -> str:
    value = html.unescape(value)
    if m := _RE_DESCRIPTION.fullmatch(value):
        return m.group(1)
    return value


def _duration(value: str) -> dt.timedelta:
    m = map(float, reversed(value.split(":")))
    s = sum(x * k for x, k in zip(m, [1, 60, 3600]))
    return dt.timedelta(seconds=s)


def _date(value: str) -> dt.date:
    return dt.datetime.strptime(value, "%d.%m.%Y").date()


@dc.dataclass
class ProductCategory:
    """Категория"""

    id: int
    """Идентификатор"""
    title: HtmlStr
    """Название"""


@dc.dataclass(kw_only=True)
class EntityBase:
    """Базовый класс сущности API"""

    id: int
    """Идентификатор"""
    title: HtmlStr | None = None
    """Название"""
    url: UrlStr
    """URL страницы с описанием"""
    created: dt.datetime
    """Дата и время создания записи"""
    modified: dt.datetime
    """Дата и время последнего изменения"""

    class Config(BaseConfig):
        aliases = {
            "author_id": "authorId",
            "author_ids": "authorIds",
            "created": "dateCreated",
            "duration": "time",
            "end_date": "endDate",
            "filename": "originalFileName",
            "import_ids": "importIds",
            "modified": "dateModified",
            "name": "realName",
            "num_images": "picturesQuantity",
            "num_tunes": "tunesQuantity",
            "original_url": "originalUrl",
            "party_id": "partyId",
            "party_place": "partyPlace",
            "start_date": "startDate",
            "title_internal": "internalTitle",
        }

        serialization_strategy = {
            dt.date: {"deserialize": _date},
            dt.datetime: {"deserialize": dt.datetime.fromtimestamp},
            dt.timedelta: {"deserialize": _duration},
            HtmlStr: {"deserialize": _unescape},
            UrlStr: {"deserialize": unquote},
        }


@dc.dataclass(kw_only=True)
class MediaBase(EntityBase):
    """Базовый класс медиафайла"""

    party_id: int | None = None
    """Идентификатор мероприятия"""
    compo: str | None = None
    """Тип"""
    party_place: int | None = None
    """Занятое место на мероприятии"""
    author_ids: list[int]
    """Идентификаторы авторов"""
    tags: list[str] | None = None
    """Теги"""
    type: str | None = None
    """Тип файла"""
    rating: Decimal
    """Рейтинг"""
    year: int | None = None
    """Год написания"""
    description: HtmlStr | None = None
    """Описание"""
    original_url: UrlStr | None = None
    """URL оригинального файла"""
    media_url: UrlStr | None = None
    """URL стандартного медиа файла"""

    @classmethod
    def __pre_deserialize__(cls, x: dict[Any, Any]) -> dict[Any, Any]:
        if url := (x.pop("mp3FilePath", None) or x.pop("imageUrl", None)):
            x["media_url"] = url
        return x


@dc.dataclass(kw_only=True)
class Tune(MediaBase):
    """Мелодия"""

    title_internal: HtmlStr | None = None
    """Внутреннее название"""
    duration: dt.timedelta | None = None
    """Длительность"""
    plays: int | None = None
    """Кол-во прослушиваний"""
    filename: UrlStr | None = None
    """Имя оригинального файла"""


@dc.dataclass(kw_only=True)
class Image(MediaBase):
    """Изображение"""

    views: int | None = None
    """Кол-во просмотров"""


@dc.dataclass
class ImportID:
    """Импортированные идентификаторы автора на сторонних ресурсах."""

    zxaaa: str | None = None
    """https://zxaaa.net/"""
    demozoo: str | None = None
    """https://demozoo.org/"""
    pouet: str | None = None
    """https://www.pouet.net/"""
    spectrumcomputing: str | None = None
    """https://spectrumcomputing.co.uk/"""
    worldofspectrum: str | None = None
    """https://worldofspectrum.net/"""
    vtrd: str | None = None
    """https://vtrd.in/"""
    zxdemo: str | None = None
    """https://zxdemo.org/"""
    speccy: str | None = None
    """https://speccy.info/"""

    class Config(BaseConfig):
        aliases = {
            "zxaaa": "3a",
            "demozoo": "dzoo",
            "spectrumcomputing": "sc",
            "worldofspectrum": "wos",
            "vtrd": "vt",
            "zxdemo": "zxd",
            "speccy": "swiki",
        }


@dc.dataclass(kw_only=True)
class AuthorAlias(EntityBase):
    """Модель псевдонима автора"""

    author_id: int | None = None
    """Идентификатор настоящего автора"""
    import_ids: ImportID | None = None
    """Идентификаторы на других ресурсах"""
    start_date: dt.date | None = None
    """Дата начала действия"""
    end_date: dt.date | None = None
    """Дата окончания действия"""


@dc.dataclass(kw_only=True)
class Author(EntityBase):
    """Модель категории"""

    name: str | None = None
    """Настоящее имя"""
    country: str | None = None
    """Страна"""
    city: str | None = None
    """Город"""
    num_images: int = 0
    """Количество изображений"""
    num_tunes: int = 0
    """Количество мелодий"""
    aliases: list[int] | None = None
    """Идентификаторы псевдонимов"""
    import_ids: ImportID | None = None
    """Идентификаторы на других ресурсах"""


@dc.dataclass
class ApiResponse[T](DataClassDictMixin):
    """Модель ответа на запросы"""

    total: int
    """Всего записей в базе данных"""
    start: int
    """Начальный индекс"""
    limit: int
    """Ограничение"""
    result: list[T]
    """Данные ответа"""

    class Config(BaseConfig):
        aliases = {"total": "totalAmount"}
        discriminator = Discriminator(field="entity", include_subtypes=True)
        lazy_compilation = True


@dc.dataclass
class AuthorResponse(ApiResponse[Author]):
    entity = Entity.AUTHOR


@dc.dataclass
class AuthorAliasResponse(ApiResponse[AuthorAlias]):
    entity = Entity.AUTHOR_ALIAS


@dc.dataclass
class ProductCategoryResponse(ApiResponse[ProductCategory]):
    entity = Entity.PRODUCT_CATEGORY


@dc.dataclass
class TuneResponse(ApiResponse[Tune]):
    entity = Entity.TUNE


@dc.dataclass
class ImageResponse(ApiResponse[Image]):
    entity = Entity.IMAGE
