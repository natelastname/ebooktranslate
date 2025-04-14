#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2025-04-08T20:23:36-04:00

@author: nate
"""
import warnings

import argostranslate.package
import argostranslate.translate
import bs4
import ebooklib.epub
import readabilipy as rp
import translatehtml
from loguru import logger
from lxml import etree
from translater.types import MainArgs


def get_argo_package(from_code, to_code):
    available_packages = argostranslate.package.get_available_packages()
    for pkg in available_packages:
        if pkg.from_code == from_code and pkg.to_code == to_code:
            return pkg
    raise Exception("Could not find an argo package.")

def get_languages(from_code, to_code):
    pkg = get_argo_package(from_code, to_code)
    download_path = pkg.download()
    argostranslate.package.install_from_path(download_path)
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = list(filter(lambda item: item.code == from_code, installed_languages))[0]
    to_lang = list(filter(lambda item: item.code == to_code, installed_languages))[0]
    return from_lang, to_lang

def html_items(book):
    tracks = []
    def should_skip(item):
        if isinstance(item, ebooklib.epub.EpubHtml):
            return False
        elif isinstance(item, ebooklib.epub.EpubItem):
            t0 = item.get_type()
            if t0 == ebooklib.ITEM_UNKNOWN:
                # .html ends up here
                return False
            elif t0 == ebooklib.ITEM_DOCUMENT:
                return False
            else:
                # It is something weird like an image or audio track
                return True

    for i0 in book.items:
        skip = should_skip(i0)
        if skip:
            logger.info(f'{i0} (skipped)')
            continue
        yield i0.id, i0

def xlate_html(underlying_translation, soup):
    #soup = bs4.BeautifulSoup(html_bytes, "lxml")
    itag = translatehtml.itag_of_soup(soup)
    translated_tag = translatehtml.translate_tags(underlying_translation, itag)
    translated_soup = translatehtml.soup_of_itag(translated_tag)
    return translated_soup

def translate_epub(args: MainArgs, outfile):

    from_lang, to_lang = get_languages('ru', 'en')
    translation = from_lang.get_translation(to_lang)

    opts = {"ignore_ncx": True}
    book = ebooklib.epub.read_epub(args.infile, options=opts)

    for name, item0 in html_items(book):
        # Not needed because translatehtml immediately passes the 2nd
        # arg to this constructor internally
        #soup0 = bs4.BeautifulSoup(html_bytes, 'html.parser')
        html_bytes = item0.content

        logger.info(f'Processing "{name}"...')


        soup0 = bs4.BeautifulSoup(html_bytes, 'xml').find('html')
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            res = xlate_html(translation, soup0)

        out_str = res.prettify()

        parser = etree.XMLParser()
        tree = etree.fromstring(out_str, parser=parser)

        # Convert to string with XML declaration
        out_bytes = etree.tostring(
            tree,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
            doctype="<!DOCTYPE html>"
        )
        item0.set_content(out_bytes)
        ebooklib.epub.write_epub(outfile, book)

    logger.info(__name__)
