from hypomnema.api.helpers import create_tmx
from .translation import SimpleArgosTranslator, translate_and_dump_tmx
from .translation.translate import tus_from_csv, get_header, dump_tmx
from .score import score_bleu
from pathlib import Path
from hypomnema import load, Tu
from typing import Generator


def main():
    tmx_path = Path("./open_subs_tmx.tmx")
    csv_path = Path("./tatoeba.csv")
    csv_tu_vals = {(tu.variants[0].content[0], tu.variants[1].content[0]) for tu in tus_from_csv(csv_path, "\t")}
    used_tus = []
    tus: Generator[Tu, None, None] = load(tmx_path, filter="tu")  # ty: ignore[invalid-assignment]
    header = get_header(tmx_path)
    i = 0
    for tu in tus:
        if (tu.variants[0].content[0], tu.variants[1].content[0]) not in csv_tu_vals:
            used_tus.append(tu)
        i += 1
        if i % 100 == 0:
            print(f"Processed {i} TUs")
        if i == 5000:
            break
    tmx = create_tmx(header=header, body=used_tus)
    dump_tmx(tmx)

if __name__ == "__main__":
    main()
