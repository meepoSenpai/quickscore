from hypomnema.api.helpers import create_prop, create_tuv, create_tmx, create_tu
from typing import Generator
from hypomnema import Tu, load, Header, dump, Tmx
from pathlib import Path
from .translator import AbstractTranslator
from lxml import etree

def _get_src_entry(tu: Tu, src_lang: str) -> str:
    src_tv = [tv for tv in tu.variants if tv.lang == src_lang][0]
    for c in src_tv.content:
        if isinstance(c, str):
            return c
    raise ValueError("")

def add_translation_to_tus(tmx: Path | Tmx, translator: AbstractTranslator) -> list[Tu]:
    if isinstance(tmx, Path):
        src_lang: str = load(tmx, filter="header").__next__().srclang  # ty: ignore[unresolved-attribute, invalid-assignment]
        tus: Generator[Tu, None, None] = load(tmx, filter="tu")  # ty: ignore[invalid-assignment]
    else:
        src_lang = tmx.header.srclang
        tus = (tu for tu in tmx.body)
    target_lang = None
    prop = create_prop(f"translated via {translator.__class__.__name__}", "MTranslation")
    created_tus: list[Tu] = []
    for tu in tus:
        if not target_lang:
            for variant in tu.variants:
                if variant.lang != src_lang:
                    target_lang = variant.lang
            if target_lang is None:
                raise ValueError()
        translated_text = translator.translate(
            _get_src_entry(tu, src_lang),
            src_lang,
            target_lang
        )
        tuv = create_tuv(lang=target_lang, content=[translated_text], props=[prop])
        tu.variants.append(tuv)
        created_tus.append(tu)
    return created_tus

def translate_and_dump_tmx(original_tmx_path: Path, translator: AbstractTranslator, output_path: Path = Path("./output.tmx")) -> list[Tu]:
    header = get_header(original_tmx_path)
    modified_tus = add_translation_to_tus(original_tmx_path, translator)
    tmx = create_tmx(header=header, body=modified_tus)
    dump_tmx(tmx, output_path)
    return modified_tus

def get_header(tmx_path: Path) -> Header:
    header: Header = load(tmx_path, filter="header").__next__()  # ty: ignore[invalid-assignment]
    return header

def dump_tmx(tmx: Tmx, output_path: Path = Path("./output.tmx")):
    dump(tmx, output_path)
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(str(output_path), parser)
        tree.write(
            str(output_path),
            encoding="utf-8",
            xml_declaration=True,
            pretty_print=True,
        )
    except Exception:
        pass


def tus_from_csv(csv_path: Path, delimiter: str = ",") -> list[Tu]:
    import csv
    tus: list[Tu] = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        for row in reader:
            tu = create_tu(variants=[create_tuv(lang="de", content=[row[2]]), create_tuv(lang="ru", content=[row[3]])])
            tus.append(tu)
    return tus

def tu_cmp(a: Tu, b: Tu) -> bool:
    return set([tuv.content for tuv in a.variants]) == set([tuv.content for tuv in b.variants])
