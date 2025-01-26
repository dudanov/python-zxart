import dataclasses as dc
import datetime as dt
import html
import re
from decimal import Decimal
from typing import Final, Literal
from urllib.parse import unquote

from mashumaro.mixins.orjson import DataClassORJSONMixin

_RE_DESCRIPTION = re.compile(r"<pre>(.*)</pre>", re.DOTALL)

_FIELD_ALIASES: Final = {
    "title_internal": "internalTitle",
    "created": "dateCreated",
    "modified": "dateModified",
    "duration": "time",
    "party_id": "partyId",
    "party_place": "partyPlace",
    "authors": "authorIds",
    "original_url": "originalUrl",
    "filename": "originalFileName",
    "mp3_url": "mp3FilePath",
    "image_url": "imageUrl",
    "import_ids": "importIds",
    "author_id": "authorId",
    "start_date": "startDate",
    "end_date": "endDate",
}
"""Карта соответствий полей моделей и JSON."""


def _unescape(value: str) -> str:
    value = html.unescape(value)
    if m := _RE_DESCRIPTION.fullmatch(value):
        return m.group(1)
    return value


def _duration(value: str) -> dt.timedelta:
    ms, *smh = map(int, reversed(re.split(r"[:.]", value)))
    s = sum(x * k for x, k in zip(smh, [1, 60, 3600]))
    return dt.timedelta(seconds=s, milliseconds=ms * 10)


def _date(value: str) -> dt.date:
    return dt.datetime.strptime(value, "%d.%m.%Y").date()


_meta_duration: Final = {"deserialize": _duration}
_meta_unescape: Final = {"deserialize": _unescape}
_meta_unquote: Final = {"deserialize": unquote}
_meta_datetime: Final = {"deserialize": dt.datetime.fromtimestamp}
_meta_date: Final = {"deserialize": _date}


@dc.dataclass
class ProductCategory:
    """Модель категории"""

    id: int
    """Идентификатор"""
    title: str = dc.field(metadata=_meta_unescape)
    """Название"""


@dc.dataclass(kw_only=True)
class EntityModel:
    """Базовая модель сущности."""

    id: int
    """Идентификатор"""
    title: str | None = dc.field(default=None, metadata=_meta_unescape)
    """Название"""
    url: str
    """URL страницы с описанием"""
    created: dt.datetime = dc.field(metadata=_meta_datetime)
    """Дата и время создания записи"""
    modified: dt.datetime = dc.field(metadata=_meta_datetime)
    """Дата и время последнего изменения"""

    class Config:
        aliases = _FIELD_ALIASES


@dc.dataclass(kw_only=True)
class Media(EntityModel):
    party_id: int | None = None
    """Идентификатор мероприятия"""
    compo: str | None = None
    """Тип"""
    party_place: int | None = None
    """Занятое место на мероприятии"""
    authors: list[int]
    """Идентификаторы авторов"""
    tags: list[str] | None = None
    """Теги"""
    type: str | None = None
    """Тип файла"""
    rating: Decimal
    """Рейтинг"""
    year: int | None = None
    """Год написания"""
    description: str | None = dc.field(default=None, metadata=_meta_unescape)
    """Описание"""
    original_url: str | None = dc.field(default=None, metadata=_meta_unquote)
    """URL оригинального файла"""


@dc.dataclass(kw_only=True)
class Music(Media):
    """Модель музыкальной композиции"""

    title_internal: str | None = dc.field(default=None, metadata=_meta_unescape)
    """Внутреннее название"""
    duration: dt.timedelta | None = dc.field(default=None, metadata=_meta_duration)
    """Длительность"""
    plays: int | None = None
    """Кол-во прослушиваний"""
    filename: str | None = dc.field(default=None, metadata=_meta_unquote)
    """Имя оригинального файла"""
    mp3_url: str | None = None
    """URL файла MP3"""


@dc.dataclass(kw_only=True)
class Picture(Media):
    """Модель изображения"""

    image_url: str | None = None
    """URL изображения"""
    views: int | None = None
    """Кол-во прослушиваний"""


@dc.dataclass
class ImportID:
    """Модель категории"""

    zxaaa: str | None = dc.field(default=None, metadata={"alias": "3a"})
    dzoo: str | None = None
    pouet: str | None = None
    sc: str | None = None
    wos: str | None = None
    vt: str | None = None
    zxd: str | None = None
    swiki: str | None = None


@dc.dataclass(kw_only=True)
class AuthorAlias(EntityModel):
    """Модель псевдонима автора"""

    author_id: int | None = None
    """Идентификатор настоящего автора"""
    import_ids: ImportID | None = None
    """Идентификаторы на других ресурсах"""
    start_date: dt.date | None = dc.field(default=None, metadata=_meta_date)
    """Дата начала действия"""
    end_date: dt.date | None = dc.field(default=None, metadata=_meta_date)
    """Дата окончания действия"""


@dc.dataclass(kw_only=True)
class Author(EntityModel):
    """Модель категории"""

    realName: str | None = None
    """Настоящее имя"""
    country: str | None = None
    """Страна"""
    city: str | None = None
    """Город"""
    picturesQuantity: int | None = None
    """Количество изображений"""
    tunesQuantity: int | None = None
    """Количество мелодий"""
    aliases: list[int] | None = None
    """Идентификаторы псевдонимов"""
    import_ids: ImportID | None = None
    """Идентификаторы на других ресурсах"""


@dc.dataclass(kw_only=True)
class ResponseResult:
    """Модель данных ответа"""

    author: list[Author] | None = None
    """Авторы"""
    authorAlias: list[AuthorAlias] | None = None
    """Псевдонимы авторов"""
    group: list[Author] | None = None
    """Группы"""
    groupAlias: list[Author] | None = None
    """Псевдонимы групп"""
    zxMusic: list[Music] | None = None
    """Музыкальные композиции"""
    zxProd: list[Author] | None = None
    """Продукты"""
    zxRelease: list[Author] | None = None
    """Релизы"""
    zxPicture: list[Picture] | None = None
    """Изображения"""
    zxProdCategory: list[ProductCategory] | None = None
    """Категории"""


@dc.dataclass(kw_only=True)
class ResponseModel(DataClassORJSONMixin):
    """Модель ответа на запросы"""

    status: Literal["success"]
    """Статус"""
    total: int
    """Всего записей в базе данных"""
    start: int
    """Начальный индекс"""
    limit: int
    """Ограничение"""
    result: ResponseResult
    """Данные ответа"""

    class Config:
        aliases = {
            "result": "responseData",
            "status": "responseStatus",
            "total": "totalAmount",
        }
