from typing import Literal

from .common import MediaParams

ImageFormat = Literal[
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


ImageFormatGroup = Literal[
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


class ImageParams(MediaParams, total=False):
    type: ImageFormat
    format_group: ImageFormatGroup
