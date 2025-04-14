# -*- coding: utf-8 -*-
"""
Created on 2025-04-09T20:27:35-04:00

@author: nate
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from dataclass_click import argument, dataclass_click, option


@dataclass
class MainArgs:
    infile: Annotated[Path, argument()]
    #baz: Annotated[int, option()] # Required
    #bar: Annotated[int | None, option()] # Optional
