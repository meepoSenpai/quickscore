from .translation import SimpleArgosTranslator, translate_and_dump_tmx
from .score import score_bleu
from pathlib import Path


def main():
    tus = translate_and_dump_tmx(Path("./en-ru.tmx"), SimpleArgosTranslator("ru", "en"), Path("./sample.tmx"))
    print(score_bleu(tus, "en"))


if __name__ == "__main__":
    main()
