from hypomnema.api.helpers import create_prop, create_tuv, create_tmx
from typing import Generator
from hypomnema import Tu, load, Header, dump
from pathlib import Path
from .translator import AbstractTranslator

def _get_src_entry(tu: Tu, src_lang: str) -> str:
    src_tv = [tv for tv in tu.variants if tv.lang == src_lang][0]
    for c in src_tv.content:
        if isinstance(c, str):
            return c
    raise ValueError("")

def add_translation_to_tus(tmx_path: Path, translator: AbstractTranslator) -> list[Tu]:
    src_lang: str = load(tmx_path, filter="header").__next__().srclang  # ty: ignore[unresolved-attribute, invalid-assignment]
    tus: Generator[Tu, None, None] = load(tmx_path, filter="tu")  # ty: ignore[invalid-assignment]
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
    header: Header = load(original_tmx_path, filter="header").__next__()  # ty: ignore[invalid-assignment]
    modified_tus = add_translation_to_tus(original_tmx_path, translator)
    tmx = create_tmx(header=header, body=modified_tus)
    dump(tmx, output_path)

    # Try to pretty-print the written TMX using lxml if available.
    try:
        from lxml import etree  # ty: ignore[unresolved-import]

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(str(output_path), parser)

        # Write back with indentation while keeping XML declaration and DOCTYPE.
        tree.write(
            str(output_path),
            encoding="utf-8",
            xml_declaration=True,
            pretty_print=True,
            doctype="<!DOCTYPE tmx SYSTEM 'tmx14.dtd'>"
        )
    except Exception:
        # If lxml isn't available or something fails, leave the original file as produced by dump().
        pass

    return modified_tus
