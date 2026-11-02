# SPDX-FileCopyrightText: 2026 covtl-sandhi contributors
# SPDX-License-Identifier: GPL-3.0-or-later
# -*- coding: utf-8 -*-
"""Tests autonomes du package covtl-sandhi (aucun pipeline requis).

Les g2p stubs embarqués portent les tokens MESURÉS des g2p du dépôt
(lexique Wikipron pour it/es/pt/de, CMUdict pour en, règles+lexique
pour fr — cf. les docstrings des modules) : les sorties attendues
sont les formes documentées, pas des artefacts du stub.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sandhi import (  # noqa: E402
    SANDHI_LANGS,
    SANDHI_LEVELS,
    SANDHI_MODES,
    apply_sandhi,
    apply_sandhi_sampa,
    apply_sandhi_text,
    get_module,
    join_words_keys,
    sandhi_rewrite_text,
    sandhi_supported,
)
from sandhi import base  # noqa: E402
from sandhi import de, en, es, fr, it, pt  # noqa: E402


def mk_g2p(lex):
    """g2p stub : split/join par '.', lexique minuscule, ponctuation
    de fin de mot strippée (miroir du pré-traitement des g2p réels)."""
    def g2p(text, warnings=None, **kw):
        out = []
        for w in str(text or '').split():
            key = w.lower().strip('.,!?;:')
            out.append(lex.get(key, key))
        return '.'.join(out)
    g2p.lexicon = lex
    return g2p


G2P_FR = mk_g2p({
    'faut': 'fo', 'faute': 'fot', 'il': 'i', 'ils': 'i',
    'les': 'le', 'amis': 'a.mi', 'mon': 'mO~', 'monne': 'mO~n',
    'ami': 'a.mi', 'très': 'tRE', 'heureux': '2.R2',
    'enfants': 'A~.fa~', 'adorables': 'a.dO.rabl',
    'vous': 'vu', 'avez': 'a.ve', 'et': 'e', 'est': 'e',
    'grand': 'gRa~', 'grante': 'gRa~t', 'arbre': 'aR.bR',
    'héros': 'e.Ro', 'petit': 'ti', 'on': 'o~',
    'cher': 'SEr', 'encore': 'a~.kOR', 'partent': 'paRt',
})

G2P_EN = mk_g2p({
    'a': '@', 'an': 'an', 'apple': 'a.p@l', 'far': 'faR',
    'away': '@.we', 'turn': 't@Rn', 'off': 'Of', 'hour': 'a.w@R',
    'one': 'w@n', 'way': 'we', 'the': 'D@', 'end': 'End',
    'her': 'h@R', 'own': 'on', 'car': 'kaR', 'cat': 'kAt',
    'engine': 'En.dZ@n', 'university': 'ju.n@.v3.s@.ti',
})

G2P_IT = mk_g2p({
    'a': 'a', 'casa': 'ka.sa', 'città': 'tSi.tta', 'bella': 'bE.lla',
    'e': 'e', 'ed': 'ed', 'io': 'i.o', 'come': 'ko.me', 'va': 'va',
    'così': 'ko.si', 'però': 'pe.rO', 'è': 'E', 'la': 'la',
})

G2P_ES = mk_g2p({
    'los': 'los', 'amigos': 'a.mi.gos', 'y': 'i', 'e': 'e',
    'ignacio': 'i.gna.Tjo', 'un': 'un', 'águila': 'a.gi.la',
    'es': 'es', 'por': 'poR', 'amor': 'a.mor', 'la': 'la',
})

G2P_PT = mk_g2p({
    'os': 'oS', 'amigos': 'a.mi.guS', 'mil': 'mil', 'ser': 'seR',
    'útil': 'u.til', 'paz': 'pas', 'eterna': 'e.tER.na', 'a': 'a',
})

G2P_DE = mk_g2p({
    'ein': 'ajn', 'apfel': 'a.pf@l', 'das': 'das', 'ist': 'Ist',
    'ei': 'aj', 'der': 'de:R', 'alte': 'al.t@', 'mutter': 'mU.t@R',
    'haus': 'ha.s',
})


# ===========================================================================
# base
# ===========================================================================

def test_levels_and_ranks():
    assert SANDHI_LEVELS == ('off', 'minimal', 'standard', 'careful')
    for lv, rank in (('off', 0), ('minimal', 1), ('standard', 2),
                     ('careful', 3)):
        assert base.level_rank(lv) == rank
    with pytest.raises(ValueError):
        base.level_rank('bogus')


def test_join_words_keys():
    assert join_words_keys(['fo', 'ti']) == 'fo ti'
    assert join_words_keys(['ajn', ' a.pf@l']) == 'ajn a.pf@l'
    assert join_words_keys(['a', '', 'b']) == 'a b'    # slot absorbé


def test_split_final_key():
    assert base.split_final_key('wAtS') == ('wA', 'tS')
    assert base.split_final_key('faR') == ('fa', 'R')


def test_load_wordlist_fallback(tmp_path):
    # data/ du package : le fichier fr_h_aspire.txt existe et doit
    # remplacer la table embarquée ; un fichier absent retombe sur
    # le fallback
    got = base.load_wordlist('fr_h_aspire.txt',
                             frozenset({'zzz_inconnu'}))
    assert 'hamburger' in got and 'zzz_inconnu' not in got
    assert base.load_wordlist('absent.txt',
                              frozenset({'repli'})) == frozenset({'repli'})


# ===========================================================================
# registre / gateway
# ===========================================================================

def test_registry():
    assert SANDHI_LANGS == frozenset({'fr', 'en', 'it', 'es', 'de', 'pt'})
    for lg in SANDHI_LANGS:
        assert sandhi_supported(lg)
        assert get_module(lg) is not None
    assert not sandhi_supported('xx')
    assert get_module('xx') is None
    assert SANDHI_MODES == ('g2p', 'post', 'pre')


def test_gateway_unsupported_passthrough():
    g2p = mk_g2p({'hello': 'h@.lo'})
    warnings: list = []
    out = apply_sandhi_text('xx', 'hello', g2p, 'standard', 'g2p',
                            warnings)
    assert out == 'h@.lo' and any('no rule module' in w for w in warnings)


def test_gateway_bad_mode():
    with pytest.raises(ValueError):
        apply_sandhi_text('fr', 'faut il', G2P_FR, 'standard', 'bogus')


# ===========================================================================
# FR — niveaux monotones + v3 rétrocompatibilité
# ===========================================================================

def test_fr_off_identity():
    assert fr.liaison_g2p('faut il', G2P_FR, level='off') == 'fo.i'
    assert fr.liaison_g2p('mon ami', G2P_FR, level='off') == 'mO~.a.mi'


def test_fr_minimal_obligatoire():
    # déterminant + pronom : catégorique
    assert fr.liaison_g2p('les amis', G2P_FR, level='minimal') \
        == 'le.za.mi'
    assert fr.liaison_g2p('mon ami', G2P_FR, level='minimal') \
        == 'mO~.na.mi'


def test_fr_minimal_exclut_courante():
    # « faut » = modal → classe COURANTE (standard), pas minimal
    assert fr.liaison_g2p('faut il', G2P_FR, level='minimal') == 'fo.i'
    assert fr.liaison_g2p('faut il', G2P_FR, level='standard') == 'fo.til'


def test_fr_v3_none_est_standard():
    for text in ('faut il', 'les amis', 'mon ami', 'vous avez'):
        assert fr.liaison_g2p(text, G2P_FR) \
            == fr.liaison_g2p(text, G2P_FR, level='standard')


def test_fr_careful_pluriel():
    # « enfants adorables » : nom pluriel hors _TRIGGERS → careful
    assert fr.liaison_g2p('enfants adorables', G2P_FR,
                          level='standard') == 'A~.fa~.a.dO.rabl'
    assert fr.liaison_g2p('enfants adorables', G2P_FR,
                          level='careful') == 'A~.fa~.za.dO.rabl'


def test_fr_careful_exclut_formes_verbales():
    # « partent » (verbe, -ent) : jamais liaison, même careful
    g2p = mk_g2p({'partent': 'paRt', 'encore': 'a~.kOR'})
    assert fr.liaison_g2p('partent encore', g2p, level='careful') \
        == 'paRt.a~.kOR'


def test_fr_h_aspire_blocker():
    g2p = mk_g2p({'les': 'le', 'héros': 'e.Ro'})
    assert fr.liaison_g2p('les héros', g2p, level='careful') \
        == 'le.e.Ro'


def test_fr_decide_pair():
    assert fr.decide_pair('faut', 'il', 'fo', 'i',
                          level='standard') == ('fo', 'ti')
    assert fr.decide_pair('faut', 'il', 'fo', 'i',
                          level='minimal') is None
    assert fr.decide_pair('enfants', 'adorables', 'A~.fa~', 'a.dO.rabl',
                          level='careful') == ('A~.fa~', 'za.dO.rabl')


def test_fr_modes_pre_post():
    assert fr.apply_liaison_pre('faut il', G2P_FR) == 'faute il'
    # post : insertion seule — hérite le token du g2p de base ('i')
    assert fr.apply_liaison_post('faut il', 'fo.i', G2P_FR,
                                 level='standard') == 'fo.ti'


def test_fr_pas_a_travers_virgule():
    g2p = mk_g2p({'les': 'le', 'amis': 'a.mi', 'cherchent': 'SErS',
                  'encore': 'a~.kOR'})
    out = fr.liaison_g2p('les amis, cherchent encore', g2p,
                         level='careful')
    # liaison dans la 1re partie, JAMAIS à travers la virgule
    assert out == 'le.za.mi.SErS.a~.kOR'


# ===========================================================================
# EN
# ===========================================================================

def test_en_an_minimal():
    assert en.liaison_g2p('a apple', G2P_EN, level='off') == '@.a.p@l'
    assert en.liaison_g2p('a apple', G2P_EN, level='minimal') \
        == '@.na.p@l'


def test_en_an_test_phonetique():
    # hour → a.w@R (voyelle) : an ; one → w@n (consonne) : pas de n
    assert en.liaison_g2p('a hour', G2P_EN, level='minimal') \
        == '@.na.w@R'
    assert en.liaison_g2p('a one way', G2P_EN, level='careful') \
        == '@.w@n.we'


def test_en_onset_linking_standard():
    assert en.liaison_g2p('far away', G2P_EN, level='minimal') \
        == 'faR.@.we'
    assert en.liaison_g2p('far away', G2P_EN, level='standard') \
        == 'fa.R@.we'
    assert en.liaison_g2p('turn off', G2P_EN, level='standard') \
        == 't@R.nOf'
    assert en.liaison_g2p('car engine', G2P_EN, level='standard') \
        == 'ka.REn.dZ@n'


def test_en_pas_de_link_apres_voyelle():
    # the → D@ (fin vocalique) : rien à déplacer
    assert en.liaison_g2p('the end', G2P_EN, level='careful') \
        == 'D@.End'


def test_en_decide_pair_et_pre():
    assert en.decide_pair('a', 'apple', '@', 'a.p@l',
                          level='minimal') == ('@', 'na.p@l')
    assert en.decide_pair('far', 'away', 'faR', '@.we',
                          level='standard') == ('fa', 'R@.we')
    assert en.apply_liaison_pre('a apple', G2P_EN, level='minimal') \
        == 'an apple'
    # onset linking : pas de graphie → warning, texte intact
    warns: list = []
    out = en.apply_liaison_pre('far away', G2P_EN, level='standard',
                               warnings=warns)
    assert out == 'far away' and any('onset linking' in w for w in warns)


# ===========================================================================
# IT
# ===========================================================================

def test_it_rs_et_d():
    assert it.liaison_g2p('a casa', G2P_IT, level='off') == 'a.ka.sa'
    assert it.liaison_g2p('a casa', G2P_IT, level='minimal') \
        == 'a.kka.sa'
    assert it.liaison_g2p('e io', G2P_IT, level='minimal') == 'e.di.o'


def test_it_oxyton_standard():
    assert it.liaison_g2p('città bella', G2P_IT, level='minimal') \
        == 'tSi.tta.bE.lla'
    assert it.liaison_g2p('città bella', G2P_IT, level='standard') \
        == 'tSi.tta.bbE.lla'
    assert it.liaison_g2p('come va', G2P_IT, level='minimal') \
        == 'ko.me.va'
    assert it.liaison_g2p('come va', G2P_IT, level='standard') \
        == 'ko.me.vva'


def test_it_careful_egale_standard():
    assert it.liaison_g2p('città bella', G2P_IT, level='careful') \
        == it.liaison_g2p('città bella', G2P_IT, level='standard')


def test_it_decide_pair():
    assert it.decide_pair('a', 'casa', 'a', 'ka.sa',
                          level='minimal') == ('a', 'kka.sa')
    assert it.decide_pair('e', 'io', 'e', 'i.o',
                          level='minimal') == ('e', 'di.o')


# ===========================================================================
# ES
# ===========================================================================

def test_es_alt_minimal_enlace_standard():
    assert es.liaison_g2p('los amigos', G2P_ES, level='minimal') \
        == 'los.a.mi.gos'
    assert es.liaison_g2p('los amigos', G2P_ES, level='standard') \
        == 'lo.sa.mi.gos'
    assert es.liaison_g2p('y ignacio', G2P_ES, level='minimal') \
        == 'e.i.gna.Tjo'


def test_es_decide_pair():
    assert es.decide_pair('los', 'amigos', 'los', 'a.mi.gos',
                          level='standard') == ('lo', 'sa.mi.gos')


# ===========================================================================
# PT
# ===========================================================================

def test_pt_encadeamento():
    assert pt.liaison_g2p('os amigos', G2P_PT, level='minimal') \
        == 'o.Za.mi.guS'
    assert pt.liaison_g2p('os amigos', G2P_PT, level='standard') \
        == 'o.Za.mi.guS'
    # « mil » n'est pas un mot-outil → standard seulement
    assert pt.liaison_g2p('mil amigos', G2P_PT, level='minimal') \
        == 'mil.a.mi.guS'
    assert pt.liaison_g2p('mil amigos', G2P_PT, level='standard') \
        == 'mi.la.mi.guS'


def test_pt_decide_pair():
    assert pt.decide_pair('os', 'amigos', 'oS', 'a.mi.guS',
                          level='standard') == ('o', 'Za.mi.guS')


# ===========================================================================
# DE
# ===========================================================================

def test_de_glottal_levels():
    # W2 = 'Apfel' après 'ein' (déterminant) : minimal
    assert de.liaison_g2p('ein Apfel', G2P_DE, level='minimal') \
        == 'ajn a.pf@l'
    assert de.liaison_g2p('ein Apfel', G2P_DE, level='standard') \
        == 'ajn a.pf@l'


def test_de_careful_leve_exemption():
    # standard : frontière devant 'Ei' seul ('ein' est exempté) ;
    # careful : frontière aussi devant 'ein' (mot-outil)
    std = de.liaison_g2p('das ist ein Ei', G2P_DE, level='standard')
    care = de.liaison_g2p('das ist ein Ei', G2P_DE, level='careful')
    assert std.count(' ') == 1
    assert care.count(' ') == 2


def test_de_decide_pair():
    assert de.decide_pair('ein', 'Apfel', 'ajn', 'a.pf@l',
                          level='standard') == ('ajn', ' a.pf@l')


# ===========================================================================
# bas niveau + chemin expressif
# ===========================================================================

def test_apply_sandhi_six_langues():
    assert apply_sandhi('fr', ['faut', 'il'], ['fo', 'i'],
                        'standard') == ['fo', 'ti']
    assert apply_sandhi('en', ['far', 'away'], ['faR', '@.we'],
                        'standard') == ['fa', 'R@.we']
    assert apply_sandhi('it', ['a', 'casa'], ['a', 'ka.sa'],
                        'standard') == ['a', 'kka.sa']
    assert apply_sandhi('es', ['los', 'amigos'], ['los', 'a.mi.gos'],
                        'standard') == ['lo', 'sa.mi.gos']
    assert apply_sandhi('pt', ['os', 'amigos'], ['oS', 'a.mi.guS'],
                        'standard') == ['o', 'Za.mi.guS']
    assert apply_sandhi('de', ['ein', 'Apfel'], ['ajn', 'a.pf@l'],
                        'standard') == ['ajn', ' a.pf@l']


def test_apply_sandhi_off_and_lengths():
    assert apply_sandhi('fr', ['a', 'b'], ['x', 'y'], 'off') == ['x', 'y']
    with pytest.raises(ValueError):
        apply_sandhi('fr', ['a'], ['x', 'y'], 'standard')


def test_expressive_jamais_a_travers_pause():
    # marqueur de respiration '%' : la paire ne fusionne pas
    out = apply_sandhi_sampa('fr', 'mon ami', 'mO~.%.a.mi', G2P_FR,
                             'standard', 'g2p')
    assert '%' in out
    # sans pause : fusion normale
    out = apply_sandhi_sampa('fr', 'mon ami', 'mO~.a.mi', G2P_FR,
                             'standard', 'g2p')
    assert out == 'mO~.na.mi'


def test_rewrite_text_pre():
    assert sandhi_rewrite_text('en', 'a apple', G2P_EN,
                               'minimal') == 'an apple'
    assert sandhi_rewrite_text('fr', 'faut il', G2P_FR,
                               'standard') == 'faute il'


def test_sans_paire_identite():
    # phrase sans AUCUNE paire : tous modes/niveaux = g2p de base
    cases = (
        ('fr', G2P_FR, 'mon cher ami'),
        ('en', G2P_EN, 'the cat'),
        ('it', G2P_IT, 'la casa'),
        ('es', G2P_ES, 'la casa'),
        ('pt', G2P_PT, 'a casa'),
        ('de', G2P_DE, 'das haus'),
    )
    for lang, g2p, text in cases:
        base_out = g2p(text)
        for mode in SANDHI_MODES:
            assert apply_sandhi_text(lang, text, g2p, 'careful',
                                     mode) == base_out, (lang, mode)
