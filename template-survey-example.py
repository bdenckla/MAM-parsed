""" Exports main. """

import collections
import json
import os

_MINIROW = collections.namedtuple('Minirow', 'D, CP, EP')
_SUBTYPE_FNS = {  # wte: Wikitext element (str or single-item dict)
    'tmpl': lambda wte: wte[0][0],
    'custom_tag': lambda wte: wte,
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
    fun = _SUBTYPE_FNS[key]
    return fun(wtel[key])


def _record(survey, wtel, psv_psn, column_letter):
    if isinstance(wtel, str):
        return
    assert isinstance(wtel, dict)
    wtel_keys = tuple(wtel.keys())
    assert len(wtel_keys) == 1
    wtel_key = wtel_keys[0]
    key = (
        wtel_key,
        _subtype(wtel_key, wtel),
        _category(psv_psn),
        column_letter)
    survey[key] += 1
    if wtel_key == 'tmpl':
        for arg in wtel['tmpl'][1:]:  # e.g. for a, b, c in {{f|a|b|c}}
            for arg_wtel in arg:
                _record(survey, arg_wtel, psv_psn, column_letter)
    return


def _keyfn(record):
    return tuple(record.values())


def _do_survey(sec_body):
    # chapent: chaptered entity (book or sub-book)
    survey = collections.defaultdict(int)
    for chapent in sec_body:
        for chapter in chapent['chapters'].values():
            for pseudoverse in chapter.items():
                psv_psn, psv_contents = pseudoverse
                minirow = _MINIROW(*psv_contents)
                for wikitext_el in minirow.CP:
                    _record(survey, wikitext_el, psv_psn, 'C')
                for wikitext_el in minirow.EP:
                    _record(survey, wikitext_el, psv_psn, 'E')
    return survey


def _reformat_survey(survey):
    records = []
    for key, count in survey.items():
        rec = {
            'wtel_type': key[0],
            'wtel_subtype': key[1],
            'pseudoverse_category': key[2],
            'column_letter': key[3],
            'count': count}
        records.append(rec)
    return sorted(records, key=_keyfn)


def main():
    """ Surveys the templates used in Torah. """
    with open('plain/BA-Samuel.json', encoding='utf-8') as fpi:
        book24 = json.load(fpi)
    survey = _do_survey(book24['book39s'])
    records = _reformat_survey(survey)
    with _openw('./template-survey-example-out.json') as fpo:
        dump_opts = {'indent': 0, 'ensure_ascii': False}
        json.dump(records, fpo, **dump_opts)


if __name__ == "__main__":
    main()
