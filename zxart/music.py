from typing import Literal

from .common import MediaOptions

MusicFormat = Literal[
    "AKS",
    "AS0",
    "ASC",
    "AY",
    "CHI",
    "CHP",
    "COP",
    "DMM",
    "DST",
    "ET1",
    "FTC",
    "FUR",
    "GTR",
    "MOD",
    "MP3",
    "MTC",
    "PDT",
    "PSC",
    "PSG",
    "PSM",
    "PT1",
    "PT2",
    "PT3",
    "SQD",
    "SQT",
    "ST1",
    "ST3",
    "STC",
    "STP",
    "STR",
    "TF0",
    "TFC",
    "TFD",
    "TFE",
    "TS",
    "VGM",
    "VTX",
    "WAV",
    "YM",
]


MusicFormatGroup = Literal[
    "ay",
    "beeper",
    "digitalbeeper",
    "beeperdigitalbeeper",
    "digitalay",
    "ts",
    "fm",
    "tsfm",
    "aybeeper",
    "aydigitalay",
    "aycovox",
    "saa",
]


class MusicOptions(MediaOptions, total=False):
    format: MusicFormat
    format_group: MusicFormatGroup


class PictureOptions(MediaOptions, total=False):
    type: MusicFormat
    format_group: MusicFormatGroup
