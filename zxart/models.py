import dataclasses as dc
import datetime as dt
import html
import re
from decimal import Decimal
from typing import Final, Literal
from urllib.parse import unquote

from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin

_RE_DESCRIPTION = re.compile(r"<pre>(.*)</pre>", re.DOTALL)


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


_meta_unescape: Final = {"deserialize": _unescape}
_meta_unquote: Final = {"deserialize": unquote}


@dc.dataclass
class ProductCategory:
    """Модель категории"""

    id: int
    """Идентификатор"""
    title: str = dc.field(metadata=_meta_unescape)
    """Название"""


@dc.dataclass(kw_only=True)
class EntityBase:
    """Базовая модель сущности."""

    id: int
    """Идентификатор"""
    title: str | None = dc.field(default=None, metadata=_meta_unescape)
    """Название"""
    url: str
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
            "image_url": "imageUrl",
            "import_ids": "importIds",
            "modified": "dateModified",
            "mp3_url": "mp3FilePath",
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
            dt.datetime: {"deserialize": dt.datetime.fromtimestamp},
            dt.date: {"deserialize": _date},
            dt.timedelta: {"deserialize": _duration},
        }


@dc.dataclass(kw_only=True)
class Media(EntityBase):
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
    description: str | None = dc.field(default=None, metadata=_meta_unescape)
    """Описание"""
    original_url: str | None = dc.field(default=None, metadata=_meta_unquote)
    """URL оригинального файла"""


@dc.dataclass(kw_only=True)
class Music(Media):
    """Модель музыкальной композиции"""

    title_internal: str | None = dc.field(default=None, metadata=_meta_unescape)
    """Внутреннее название"""
    duration: dt.timedelta | None = None
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


@dc.dataclass(kw_only=True)
class ResponseData:
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
class Response(DataClassORJSONMixin):
    """Модель ответа на запросы"""

    status: Literal["success"]
    """Статус"""
    total: int
    """Всего записей в базе данных"""
    start: int
    """Начальный индекс"""
    limit: int
    """Ограничение"""
    data: ResponseData
    """Данные ответа"""

    class Config(BaseConfig):
        aliases = {
            "data": "responseData",
            "status": "responseStatus",
            "total": "totalAmount",
        }

        lazy_compilation = True
