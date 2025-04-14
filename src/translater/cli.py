#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-04-09T20:25:10-04:00

@author: nate
"""
import asyncio
import atexit
import datetime
import json
import os
import re
import subprocess as sp
import sys

import rich_click as click
import translater
from dataclass_click import argument, dataclass_click, option
from loguru import logger
from translater.types import MainArgs


def gen_basename(infile):
    #basename_orig = os.path.basename(infile)
    #basename_orig = re.sub('[^A-Za-z0-9]+', '', basename_orig)
    basename = re.sub("\\W", '', infile)
    m0 = re.match('(\\w+)', basename)
    basename = m0.groups()[0]
    return basename


@click.command()
@dataclass_click(MainArgs)
def run0(args: MainArgs):
    logger.info("Running...")
    infile = str(args.infile)
    outpath = os.path.dirname(infile)

    basename = os.path.basename(infile)
    if basename.endswith('.epub'):
        basename = basename.split('.')[0:-1]
        basename = '.'.join(basename)

    basename = gen_basename(basename)
    outpath = os.path.join(outpath, basename)
    outfile = os.path.join(outpath, basename+'.epub')

    logger.info(f'Outfile: "{outfile}"')


    os.makedirs(outpath, exist_ok=True)

    translater.util.translate_epub(args, outfile)
