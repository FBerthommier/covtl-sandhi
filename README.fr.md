# covtl-sandhi — sandhi inter-mots pour les langues du pipeline COVTL

Package autonome de règles de **sandhi inter-mots** (les phénomènes
phonologiques de frontière de mot qu'un g2p strictement mot-à-mots ne
peut pas produire) pour les six langues du
[covtl-pipeline](https://github.com/FBerthommier/covtl-pipeline) :
**fr, en, it, es, pt, de**. Stdlib seule — aucun import du pipeline,
aucune dépendance.

| langue | phénomène | exemple | module |
|---|---|---|---|
| fr | consonne latente (liaison) | « faut il » → `fo.til`, « mon ami » → `mO~.na.mi` | `sandhi/fr.py` |
| en | a→an + onset linking / linking-r | « a apple » → `@.na.p@l`, « far away » → `fa.R@.we` | `sandhi/en.py` |
| it | raddoppiamento sintattico + *d* eufonico | « a casa » → `a.kka.sa`, « e io » → `e.di.o` | `sandhi/it.py` |
| es | enlace + alternance y→e / o→u | « los amigos » → `lo.sa.mi.gos`, « y Ignacio » → `e.i.gna.Tjo` | `sandhi/es.py` |
| pt | encadeamento + sonorisation EP | « os amigos » → `o.Z@.mi.guS` | `sandhi/pt.py` |
| de | Glottalversatz (anti-liaison) | « ein Apfel » → `ajn a.pf@l` | `sandhi/de.py` |

Le moteur de synthèse n'est **jamais** touché : les modules vivent
dans la couche texte/g2p, ne réécrivent que le texte ou le SAMPA, et
composent avec le patch prosody expressif du pipeline (la clé de
sandhi est toujours une consonne — jamais un noyau — les plans F0
restent alignés ; jamais d'insertion à travers une pause).

---

## Architecture : Branch A (hook) + Branch B (ce package)

```
covtl-pipeline                     covtl-sandhi (Branch B)
┌──────────────────────────┐      ┌───────────────────────────┐
│ vtl_synth/utils/sandhi/  │◄─copi┤ sandhi/  (règles complètes)│
│  __init__.py  (STUB)     │  ou  │  fr en it es pt de + base │
│  SANDHI_FULL = False     │  pip │  data/*.txt (vues)        │
│  → identité pure         │      └───────────────────────────┘
│  --sandhi/--sandhi-mode  │
└──────────────────────────┘
```

* **Branch A** = le patch git `patch/covtl-pipeline-sandhi-hook.patch`
  (fourni dans le zip) : il ajoute au pipeline le dossier
  `vtl_synth/utils/sandhi/` (un **stub** : `SANDHI_FULL = False`,
  toutes les entrées sont l'identité) et les options
  `--sandhi`/`--sandhi-mode`. **Sans Branch B, les sorties du
  pipeline sont bit-identiques** à celles du dépôt sans patch — le
  hook est invisible par défaut (`--sandhi off`).
* **Branch B** = ce package : les règles. Deux façons de l'activer :
  1. **copie directe** (recommandée pour rester autonome) — le
     dossier du stub existe DÉJÀ, on copie le CONTENU (notez le
     ``/.`` : sans lui, ``cp -r sandhi/ dst/`` imbriquerait le
     dossier un niveau trop profond) :
     ```bash
     cp -r sandhi/.  <pipeline>/vtl_synth/utils/sandhi/
     ```
     le package écrase le stub, le hook trouve `SANDHI_FULL = True` ;
  2. **pip** : `pip install .` — le hook détecte `import sandhi`
     (site-packages) si le stub n'a pas été remplacé.

Le hook résout dans cet ordre : stub remplacé (copie) → package pip
→ stub (identité + un avertissement par `run()` si `--sandhi` est
demandé sans package).

## Installation

```bash
# 1) pipeline vierge + hook (Branch A)
git clone https://github.com/FBerthommier/covtl-pipeline.git
cd covtl-pipeline
git apply patch/covtl-pipeline-sandhi-hook.patch
pip install -e .                      # (comme pour le dépôt nu)

# 2a) activer les règles : copie du package (Branch B)
#     (le dossier du stub existe déjà — on copie le CONTENU, notez le "/.")
cp -r sandhi/. vtl_synth/utils/sandhi/
# 2b) …ou pip
pip install /chemin/vers/covtl-sandhi-v0.1.0
```

Test rapide (après 2a/2b) :

```bash
vtl-synth run "faut il"   -l fr --sandhi standard --no-video -o out  # fo.til
vtl-synth run "a apple"   -l en --sandhi standard --no-video -o out  # @.na.p@l
vtl-synth run "los amigos" -l es --sandhi standard --no-video -o out # lo.sa.mi.gos
vtl-synth run "os amigos"  -l pt --sandhi standard --no-video -o out # o.Z@.mi.guS
vtl-synth run "ein Apfel"  -l de --sandhi standard --no-video -o out # ajn a.pf@l
```

## Les niveaux de couverture (`--sandhi`)

Le niveau est un **filtre monotone** sur la table de chaque langue :
`minimal ⊆ standard ⊆ careful`. Il ne change **jamais la
phonologie** d'une règle qui tire — seulement la classe de paires qui
ont le droit de tirer (cf. `sandhi/base.py`).

| niveau | fr | en | it | es | pt | de |
|---|---|---|---|---|---|---|
| `minimal` | liaisons obligatoires : déterminants, pronoms, copules/auxiliaires | a→an | *d* eufonico + déclencheurs monosyllabiques du RS | alternances y→e, o→u | encadeamento après mots-outils | Glottalversatz après article/déterminant |
| `standard` (défaut API) | + classe courante : adverbes, prépositions, négation, adjectifs antéposés, modaux | + onset linking / linking-r | + RS complet : oxytons, come/dove/qualche | + enlace | + encadeamento partout (voicing inclus) | + devant tout mot lexical à initiale vocalique |
| `careful` | + style soutenu : liaison après nom/adjectif pluriel (heuristique -s/-x documentée) | = standard | = standard | = standard | = standard | + devant les mots-outils aussi (hyperarticulation) |

Les cases « = standard » sont **assumées et documentées** : là où la
langue n'a pas de règle registre-dépendante fiable, `careful` égale
`standard` — jamais de différence silencieuse.

Défauts : CLI `--sandhi off` (bit-identique), API Python
`level='standard'`. Les fonctions `liaison_*` historiques (v1–v3)
appelées **sans** niveau reproduisent exactement le comportement du
patch 5 langues.

## Les trois modes (`--sandhi-mode`) — les implémentations historiques en option

| mode | principe | défaut |
|---|---|---|
| `g2p` | passerelle consciente du sandhi : oracle per-word + fusion SAMPA avec tokens corrigés (recommandé, le plus fidèle) | ✔ |
| `post` | post-processeur SAMPA pur : le g2p de base reste totalement intact | |
| `pre` | réécriture orthographique AVANT le g2p (le plus découplé, le moins fidèle — no-op documenté pour de/en) | |

## API Python

```python
from sandhi import (SANDHI_LEVELS, sandhi_supported, apply_sandhi,
                    apply_sandhi_text, sandhi_rewrite_text,
                    apply_sandhi_sampa, sandhi_oracle, join_words_keys)

sandhi_supported('fr')                      # True (fr/en/it/es/pt/de)

# passerelle sur un texte (chemin monotone — l'entrée du hook)
sampa = apply_sandhi_text('fr', 'faut il', g2p, level='standard',
                          mode='g2p')       # 'fo.til'

# bas niveau : clés par mot, APRÈS le g2p per-word (fusion dans les slots)
keys = apply_sandhi('es', ['los', 'amigos'], ['los', 'a.mi.gos'],
                    'standard')             # ['lo', 'sa.mi.gos']
phrase = join_words_keys(keys)              # 'lo.sa.mi.gos' (sep='.')

# chemin expressif : fusion dans un SAMPA déjà planifié (marqueurs
# '%' présents) — jamais à travers une pause
sampa2 = apply_sandhi_sampa('fr', 'mon ami', sampa_planifie, g2p,
                            level='standard', mode='g2p')

# mode pre seul : l'orthographe réécrite (pour nourrir le plan)
text2 = sandhi_rewrite_text('en', 'a apple', g2p, 'minimal')  # 'an apple'
```

Chaque module de langue expose en outre l'API historique complète
(`plan_pairs`, `liaison_oracle`, `apply_liaison_pre`,
`apply_liaison_post`, `liaison_g2p` — signatures v3 + `level`
optionnel) et les alias covtl-sandhi (`decide_pair`, `sandhi_g2p`,
`apply_sandhi_pre`, `apply_sandhi_post`, `sandhi_oracle`).

## Tables éditables (`sandhi/data/`)

Chaque fichier est une **vue éditable** d'une table : une entrée par
ligne, minuscules, commentaires `#`. S'il existe et n'est pas vide,
il remplace la table embarquée ; sinon la valeur par défaut s'applique
(le package reste toujours importable — ces fichiers ne sont **pas**
une dépendance).

```
data/fr_h_aspire.txt        h aspiré bloquant la liaison (fr)
data/it_rs_triggers.txt     mots-outils déclencheurs du raddoppiamento (it)
data/pt_function_words.txt  mots-outils : encadeamento minimal (pt)
data/de_glottal_exempt.txt  mots-outils exemptés de frontière glottale (de)
```

Un mot AJOUTÉ à `it_rs_triggers.txt` est de niveau `standard` ; les
sous-classes `minimal` sont embarquées dans les modules (voir leur
docstring).

## Tests

```bash
pip install pytest
python -m pytest tests/ -q
```

La suite est **autonome** (g2p stubs embarqués, aucun besoin du
pipeline) : niveaux monotones par langue, trois modes, invariants
(off = identité, pas de modification sans paire, jamais à travers
une pause), API package, data files, `decide_pair` sur les six
langues.

## Limites connues (documentées dans chaque module)

* **mode `pre`** : couverture partielle — fr : pas d'orthographe de
  repli correcte pour « est », « petit », « plus », « vieux »… ;
  de/en : le coup de glotte et l'onset linking n'ont AUCUNE graphie
  (no-op avec avertissement, utiliser g2p/post) ;
* **sinalefa** (es) / **smoothing** (en) : hors périmètre — la fusion
  de voyelles supprimerait un noyau syllabique et désalignerait les
  plans F0 du patch prosody ;
* **fr `careful`** : la frontière nom/verbe n'étant pas marquée à
  l'écrit, la liaison après pluriel est une heuristique fermée
  (-s/-x, hors terminaisons verbales -es/-ent/-ez/-ons) ;
* le module `en` suit les conventions du CMUdict gateway du pipeline
  (r britannique déjà présent dans le token : `far` → `faR`).

## Licence

GPL-3.0-or-later — voir `LICENSE` (le pipeline amont est GPL-3.0 ;
le package en dérive et reste compatible).
