from hypomnema import Tu
from sacrebleu import BLEU, CHRF, TER


def _prepare_translation_maps(
    translation_units: list[Tu],
    target_lang: str,
) -> tuple[list[str], list[str]]:
    reference_values: list[str] = []
    hypothesis_values: list[str] = []
    for tu in translation_units:
        reference = None
        hypothesis = None
        for tuv in tu.variants:
            if tuv.lang != target_lang:
                continue
            if tuv.props:
                hypothesis = tuv
            else:
                reference = tuv
        if reference and hypothesis:
            reference_values.append(reference.content[0])  # ty: ignore[invalid-argument-type]
            hypothesis_values.append(hypothesis.content[0])  # ty: ignore[invalid-argument-type]
    return hypothesis_values, reference_values


def _score_values(a: list[str], b: list[str], scorer: BLEU | CHRF | TER):
    return scorer.corpus_score(a, [b])


def score_bleu(translation_units: list[Tu], target_lang: str):
    bleu_scorer = BLEU()
    target, reference = _prepare_translation_maps(translation_units, target_lang)
    return _score_values(target, reference, bleu_scorer)


def score_ter(translation_units: list[Tu], target_lang: str):
    ter_scorer = TER()
    target, reference = _prepare_translation_maps(translation_units, target_lang)
    return _score_values(target, reference, ter_scorer)


def score_chrf(translation_units: list[Tu], target_lang: str):
    chrf_scorer = CHRF()
    target, reference = _prepare_translation_maps(translation_units, target_lang)
    return _score_values(target, reference, chrf_scorer)
