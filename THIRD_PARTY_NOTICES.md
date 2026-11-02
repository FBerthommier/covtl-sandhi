# Third-party notices — covtl-sandhi

`covtl-sandhi` is **GPL-3.0-or-later** (see `LICENSE`). It is a derivative
work of the [covtl-pipeline](https://github.com/FBerthommier/covtl-pipeline)
(GPL-3.0-or-later) and of the components below; it cannot be relicensed
under a more permissive license (MIT, Apache-2.0, BSD). Any redistribution
must keep this file, the full `LICENSE`, and — for the HTML demos — the
"Mandatory credits" notice embedded in every page.

## VocalTractLab 2.4

- Author: **Peter Birkholz** (TU Dresden) — <https://www.vocaltractlab.de>
- Role: articulatory synthesizer that produced every WAV embedded in the
  `docs/demo_liaison_*.html` pages (44.1 kHz 16-bit mono, speaker jd3).
- License: **GPL-3.0** (research use) — <https://www.vocaltractlab.de>.
- When using these demos or the package in academic work, cite
  VocalTractLab (author, version and site above) alongside the COVTL
  model references.

## vocaltractlab-cython 0.0.13

- Author: Paul Krug — <https://github.com/paul-krug/VocalTractLab-Python>
- Role: Cython binding of the VocalTractLab 2.4 API used by the upstream
  pipeline that generated the demo WAVs.
- License: GPL-3.0.

## The Berthommier COVTL model

The sandhi rules feed the COVTL articulatory model coupled with
VocalTractLab, described in:

1. F. Berthommier, "A mathematical model of the vowel space",
   arXiv:2111.00868 [eess.AS], 2021. DOI: 10.48550/arXiv.2111.00868
2. F. Berthommier, "Why can big.bi be changed to bi.gbi? A mathematical
   model of syllabification and articulatory synthesis",
   arXiv:2307.02299 [eess.AS], 2023. DOI: 10.48550/arXiv.2307.02299
3. F. Berthommier, "Synthèse de syllabes avec un modèle de Maeda piloté
   par une représentation complexe", *JEP 2024*, pp. 541–550.
   <https://aclanthology.org/2024.jeptalnrecital-jep.55/>
4. F. Berthommier, "Articulatory modeling of the S-shaped F2 trajectories
   observed in Öhman's spectrographic analysis of VCV syllables",
   *Interspeech 2025*, Rotterdam. HAL: hal-05233039,
   DOI: 10.5281/zenodo.17018832

## Pronunciation lexicons (upstream, inherited constraint)

The pipeline g2p lexicons transcribed by the Wikipron project
(CUNY-CL/wikipron, from the English Wiktionary) are **CC BY-SA 3.0**;
this package ships no lexicon, but outputs produced through the upstream
pipeline inherit that attribution for the lexicon-derived pronunciations
(see `THIRD_PARTY_NOTICES.md` of covtl-pipeline).
