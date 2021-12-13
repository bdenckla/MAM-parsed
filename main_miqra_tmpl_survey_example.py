#!/usr/bin/python3

import collections
import json
import os

_MINIROW = collections.namedtuple('Minirow', 'D, CP, EP')
_SUBTYPE_FNS = {  # wte: Wikitext element (str or single-item dict)
    'tmpl': lambda wte: wte[0][0],
    'custom_tag': lambda wte: wte,
    # 'unparseable': lambda wte: None,
}
_PSV_PSN_CATEGORIES = {
    '0': '0 (pre-chapter)',
    str('תתת'): '2 (post-chapter)'
}


def _openw(path, **kwargs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w', encoding='utf-8', **kwargs)


def _category(psv_psn):
    return _PSV_PSN_CATEGORIES.get(psv_psn) or '1 (normal verse)'


def _subtype(key, wtel):
    fn = _SUBTYPE_FNS[key]
    return fn(wtel[key])


def _record(r, wtel, psv_psn, column_letter):
    if isinstance(wtel, str):
        return
    assert isinstance(wtel, dict)
    keys = tuple(wtel.keys())
    assert len(keys) == 1
    key = keys[0]
    r[key, _subtype(key, wtel), _category(psv_psn), column_letter] += 1
    if key == 'tmpl':
        for arg in wtel['tmpl'][1:]:  # e.g. for a, b, c in {{f|a|b|c}}
            for arg_wtel in arg:
                _record(r, arg_wtel, psv_psn, column_letter)
    return


def _keyfn(record):
    return tuple(record.values())


def main():
    r = collections.defaultdict(int)
    sec_name = 'Torah'
    inpath = f'miqra-json/MAM-{sec_name}.json'
    with open(inpath, encoding='utf-8') as fpi:
        sec = json.load(fpi)
    # chapent: chaptered entity (book or sub-book)
    for chapent in sec['body']:
        for chapter in chapent['chapters'].values():
            for pseudoverse in chapter.items():
                psv_psn, psv_contents = pseudoverse
                minirow = _MINIROW(*psv_contents)
                for wikitext_el in minirow.CP:
                    _record(r, wikitext_el, psv_psn, 'C')
                for wikitext_el in minirow.EP:
                    _record(r, wikitext_el, psv_psn, 'E')
    records = []
    for key, count in r.items():
        rec = dict(
            wtel_type=key[0],
            wtel_subtype=key[1],
            pseudoverse_category=key[2],
            column_letter=key[3],
            count=count)
        records.append(rec)
    records = sorted(records, key=_keyfn)
    outpath = f'out/MAM-{sec_name}-tmpl-survey-example.json'
    with _openw(outpath) as fpo:
        dump_opts = dict(indent=0, ensure_ascii=False)
        json.dump(records, fpo, **dump_opts)


if __name__ == "__main__":
    main()
