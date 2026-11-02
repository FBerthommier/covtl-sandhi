# Changelog — covtl-sandhi

## 0.1.0 (2026-11-01)

Première release du package **covtl-sandhi** — extraction des règles
des patchs de liaison v1 (fr), v2 (fr + it) et v3 (fr/it/es/pt/de) du
dépôt [covtl-pipeline](https://github.com/FBerthommier/covtl-pipeline)
vers un package autonome, avec deux ajouts majeurs : l'**anglais** et
les **niveaux de couverture**.

### Architecture en deux branches

* **Branch A — `covtl-pipeline-sandhi-hook`** : patch git léger du
  pipeline (stub `vtl_synth/utils/sandhi/`, option `--sandhi` /
  `--sandhi-mode`). Sans le package, le hook est l'identité PURE :
  sorties bit-identiques au pipeline sans patch (vérifié sur clone
  vierge `main` @ `41f6571`, 384 tests passés / 3 échecs
  pré-existants inchangés).
* **Branch B — `covtl-sandhi` (ce package)** : les règles complètes,
  six langues. S'installe soit par `pip install .` (le hook trouve
  alors `import sandhi`), soit en COPIANT le dossier `sandhi/` par
  dessus le stub `vtl_synth/utils/sandhi/`.

### Nouveautés

* **Niveaux de couverture** `off / minimal / standard / careful`
  (option `--sandhi`, défaut CLI `off`, défaut API `standard`) :
  filtre MONOTONE sur la table de chaque langue — le niveau ne
  change jamais la phonologie d'une règle qui tire, seulement la
  classe de paires qui ont le droit de tirer :
  * `minimal` — règles catégoriques, exceptionless : fr liaisons
    obligatoires (déterminants, pronoms, copules) ; it *d eufonico* +
    déclencheurs monosyllabiques du raddoppiamento ; es alternances
    y→e / o→u ; pt encadeamento après mots-outils ; de
    Glottalversatz devant le nom qui suit l'article ; en a→an ;
  * `standard` (recommandé, = v3 exact pour fr/it/es/pt/de) —
    ajoute les règles productives : fr classe courante (adverbes,
    prépositions, adjectifs antéposés…) ; it raddoppiamento complet
    (oxytons, come/dove/qualche) ; es enlace ; pt encadeamento
    partout + voicing EP ; de frontière devant tout mot lexical ; en
    onset linking / linking-r ;
  * `careful` — registre hyperarticulé : fr style soutenu (liaison
    après nom/adjectif pluriel, heuristique -s/-x documentée) ; de
    frontière aussi devant les mots-outils ; it/es/pt/en : careful =
    standard, **dit honnêtement, jamais silencieusement**.
* **Nouveau module anglais `en`** : a→an (test PHONÉTIQUE sur le
  token — « an hour », « a one way » corrects par construction) et
  onset linking dont le linking-r (« far away » → `fa.R@.we`,
  « car engine » → `ka.REn.dZ@n`), mesurés sur le CMUdict gateway du
  pipeline. Le r britannique non prévocalique étant déjà dans le
  token CMU (`faR`), le linking-r n'est PAS une règle séparée.
* **API package** : `apply_sandhi` (bas niveau, per-word keys),
  `apply_sandhi_text` (gateway monotone, modes `g2p`/`post`/`pre`),
  `sandhi_rewrite_text` (mode pre : l'orthographe réécrite pour le
  plan expressif), `apply_sandhi_sampa` (chemin expressif, jamais à
  travers une pause `%`), `sandhi_oracle`, `join_words_keys`,
  `decide_pair` par module de langue.
* **Data files éditables** `sandhi/data/*.txt` : vues des tables
  (h aspiré, déclencheurs RS, mots-outils pt, exemption glottale de)
  — une entrée par ligne, commentaires `#`, repli = table embarquée
  (le package reste importable sans eux).
* **Rétrocompatibilité v1–v3** : les fonctions `liaison_*` historiques
  gardent leur signature ; appelées sans niveau elles reproduisent
  EXACTEMENT le comportement du patch 5 langues (v3). Le patch v3 et
  ce package sont interchangeables sur les mêmes phrases.

### Invariants (testés)

* `off` → identité bit-à-bit ; un module ne modifie jamais une phrase
  sans paire ; jamais d'insertion à travers une pause ; la clé de
  sandhi est toujours une consonne (jamais un noyau — les plans F0 du
  patch prosody restent alignés) ; le moteur de synthèse n'est jamais
  touché.

### Limites connues (documentées dans chaque module)

* mode `pre` : couverture partielle (fr : pas de repli pour « est »,
  « petit », « plus »… ; de/en : le Glottalversatz et l'onset linking
  n'ont pas de graphie → no-op avec avertissement) ;
* sinalefa es / smoothing en : hors périmètre (supprimerait un noyau
  et désalignerait les plans F0) ;
* fr `careful` : la frontière nom/verbe n'étant pas marquée à l'écrit,
  le pluriel est une heuristique -s/-x hors terminaisons verbales.
