# Reading MAM-parsed plus JSON

> **⚠ Note:** This documentation was AI-generated and is known to contain inaccuracies, but it is a lot better than no documentation.

> **Cross-references:** The per-template extraction rules documented in the `extract_text` example below are also encoded in several downstream repos. When updating those rules here, check for matching logic to propagate:
> - `mgketer/documentation/mpp-parsing.md` — AI-facing catalogue of every template decision in mgketer's MPP traversal
> - `holman-ketiv-qere/py/python_modules/mam_plus_verse_data.py` — `_collect_text_fragments` function
> - `holman-ketiv-qere/py/python_modules/qere_projection.py` — `project_qere_atoms` function

This document describes the structure of the **plus** format JSON files
in the MAM-parsed repository.

The plus format shares the same overall structure as the
[plain format](reading-mam-parsed-plain.md) but diverges in several ways.
Read the plain format documentation first for the foundation,
then use this document for the differences.

For authoritative English and Hebrew descriptions of every template, see the
[Templates tab](https://docs.google.com/spreadsheets/d/1mkQyj6by1AtBUabpbaxaZq9Z2X3pX8ZpwG91ZCSOEYs/edit?gid=1670945398#gid=1670945398)
of the MAM Google Sheet.

## Differences from plain at a glance

| Feature | Plain | Plus |
|---------|-------|------|
| Pseudo-verses `"0"` and `"תתת"` | Present | **Removed** |
| Custom XML tags (`noinclude` etc.) | Present | **Removed** |
| Wikitext line breaks (`"//"`) | Present in D column | **Removed** |
| Named params | not parsed | unified with positional |
| CP column (verse reference) | Every verse has `מ:פסוק` | Only first verse of chapter |
| `good_ending_plus` | Not present | **Added** (at book39 level) |
| Hebrew numeral help | Not present | **Added** (`he_to_int`) |
| Words with special letters | interrupted | uninterrupted provided |

## Top-level structure

Same as plain:

```json
{
  "header": {},
  "book39s": []
}
```

## Header

The plus header gains a `he_to_int` key — a mapping from every
Hebrew-numeral string that appears as a chapter or verse key in the
file to its integer equivalent. This allows consumers to navigate
chapters and verses by integer without needing to implement
Hebrew-numeral decoding.

```json
"header": {
  "book24_names": ["ספר איוב"],
  "sub_book_names": {},
  "chapter_counts": [
    { "book24_name": "ספר איוב", "sub_book_name": null, "chapter_count": 42 }
  ],
  "he_to_int": {
    "א": 1,
    "ב": 2,
    "ג": 3,
    ...
    "קעו": 176
  }
}
```

The mapping is sorted by integer value and covers the union of all
chapter and verse keys across all `book39s` in the file.
To look up, say, chapter 5 verse 12, a consumer can build the
reverse mapping once:

```python
int_to_he = {v: k for k, v in header['he_to_int'].items()}
verse_data = chapters[int_to_he[5]][int_to_he[12]]
```

## Book39 entry

The book39 entry gains a `good_ending_plus` key:

```json
{
  "book24_name": "ספר איוב",
  "sub_book_name": null,
  "good_ending_plus": null,
  "chapters": { ... }
}
```

### `good_ending_plus`

Some books in the Jewish tradition repeat the penultimate verse
after the final verse so that public reading ends on a positive note
(using the `מ:סיום בטוב` template). The `good_ending_plus` key captures this:

- `null` for most books (including Job)
- For the 4 books/book-parts that have it (Isaiah, Malachi, Lamentations,
  Ecclesiastes — note that MAM considers Malachi part of "The 12"
  Minor Prophets), it is an object with:

```json
{
  "last_chapnver": ["סו", "כד"],
  "wikitext_element": {
    "tmpl_name": "נוסח",
    "tmpl_params": {
      "1": {"tmpl_name": "מ:סיום בטוב", "tmpl_params": {"1": "..."}},
      ...
    }
  }
}
```

## Chapter structure

Same as plain — a dict keyed by Hebrew-letter chapter names — but
**without** the `"0"` (pre-chapter) and `"תתת"` (post-chapter) pseudo-verses.

So a chapter with 22 verses has exactly 22 keys (`"א"` through `"כב"`),
nothing more.

## Verse structure

Same 3-element array `[D, CP, EP]`, but with differences in each column.

### D column (index 0): Section markers

In plus, only the **first verse of each chapter** has the `מ:פסוק` template.
All other verses have an empty `[]`:

```json
// First verse (א):
[{"tmpl_name": "מ:פסוק", "tmpl_params": {"1": "איוב", "2": "א", "3": "א", "סדר": "א"}}]

// Subsequent verses (ב, ג, ...):
[]
```

(The verse identity is already encoded in the dict key,
so repeating it in CP is redundant.)

### CP column (index 1): Verse reference

Simplified compared to plain by removing `"//"` Wikitext line breaks.


### EP column (index 2): Verse text

Same mixed array of strings and template objects,
but templates use the expanded format (see below).

## Template format in plus

All templates in the plus format use the expanded representation:

```json
{
  "tmpl_name": "קו\"כ",
  "tmpl_params": {"1": "את", "2": "אַ֠תָּ֠ה"}
}
```
<!-- ltr -->

| Key | Type | Description |
|-----|------|-------------|
| `tmpl_name` | string | Template name |
| `tmpl_params` | object | Parameters — **present only when the template has params** |

Contrast with the plain format where the same template would be:

```json
{"stmpl": "קו\"כ|את|אַ֠תָּ֠ה"}
```

### `tmpl_params` keys

- Numeric string keys `"1"`, `"2"`, … correspond to positional arguments,
  with any `"2="` prefix already interpreted.
- Non-numeric keys (e.g. `"ד"`, `"ס"`, `"סדר"`) represent named parameters
  like `ד=...` in the wikitext.

The `tmpl_params` dict is absent only when the template has no parameters
(e.g. `פפ`, `סס`, `מ:פסק`).

### Template parameter values can be complex

Parameter values can themselves be:
- Strings
- Nested template objects
- Arrays of mixed strings and template objects

For a visual overview of which templates nest inside which,
see the [plus template call graphs](https://bdenckla.github.io/MAM-parsed/plus-template-call-graphs.html).

### Accessing template parameters

Use `tmpl_params` directly with the string key:

```python
def tmpl_param(tmpl, key):
    """Get a template parameter by string key (e.g. '1', '2', 'ד')."""
    return tmpl['tmpl_params'][key]
```

Example — a word with a special letter inside a ketiv-qere inside a nusach:

```json
{
  "tmpl_name": "נוסח",
  "tmpl_params": {
    "1": {
      "tmpl_name": "כו\"ק",
      "tmpl_params": {
        "1": {
          "tmpl_name": "מ:אות-מיוחדת-במילה",
          "tmpl_params": {
            "1": ["ו", {"tmpl_name": "מ:אות-ק", "tmpl_params": {"1": "ג"}}, "יש"],
            "2": "וגיש",
            "3": ".ג..",
            "4": "ק",
            "5": "ג/ק"
          }
        },
        "2": "וְג֣וּשׁ"
      }
    },
    "2": "=commentary text..."
  }
}
```

## Plus-only templates

### Special letter marking — `מ:אות-מיוחדת-במילה`

Marks a word containing a letter with a special size or form
(large, small, suspended, etc.):

```json
{
  "tmpl_name": "מ:אות-מיוחדת-במילה",
  "tmpl_params": {
    "1": ["שִׁבְ", {"tmpl_name": "מ:אות-ג", "tmpl_params": {"1": "ט֑"}}, "וֹ"],
    "2": "שִׁבְט֑וֹ",
    "3": "..ט.",
    "4": "ג",
    "5": "ט/ג"
  }
}
```

Arguments:
1. Array showing the word decomposed around the special letter, i.e. interrupted by special letters
2. The word as a plain string (uninterrupted)
3. A dot-mask showing the position of the special letter
4. The size/type code (ג = large, ק = small, ע = hung (suspended))
5. Letter/type summary

When the word is followed by a legarmeh,
the `מ:לגרמיה-2` template is included at the end of argument 1,
and the _paseq/legarmeh_ character (׀) is appended to argument 2.
Argument 3 has a dot for every letter, plus a dot for the _legarmeh_.
(E.g. Ruth 3:13 לִ֣ינִי׀, Esther 1:6 ח֣וּר׀.)

### Special ketiv-qere template (`מ:כו"ק מיוחד`)

Nine special ketiv-qere types are encoded in the required named
parameter <bdi>`סוג=`</bdi>.

<!-- ltr -->

The value given to <bdi>`סוג=`</bdi>
is a **dataset-level classification tag**: it records which structural
subtype this k/q pair belongs to, independent of any particular MAM edition.
An edition may use it for display selection — the MAM Wikisource edition, for
example, reads <bdi>`סוג=`</bdi> to choose a rendering, applying four distinct display
behaviors across the nine subtypes. Other MAM editions are free to implement
their own rendering keyed off the same <bdi>`סוג=`</bdi> values.

This template appears in both plain and plus format data.

The following `סוג=` values are used with the `מ:כו"ק מיוחד` template:


<!-- ltr -->


| Type | Meaning |
|-------------|---------|
| <bdi>כו"ק בין שני מקפים</bdi> | Ketiv-qere between two maqafim (Isaiah 26:20 only) |
| <bdi>כו"ק כתיב מילה חדה וקרי תרתין מילין</bdi> | 1-word ketiv mapped to 2-atom qere |
| <bdi>כו"ק כתיב מילה חדה וקרי תרתין מילין בין שני מקפים</bdi> | Same as above but between maqafim (1 Chronicles 9:4 only) |
| <bdi>כו"ק כתיב תרתין מילין וקרי מילה חדה</bdi> | 2-word ketiv mapped to 1-atom qere |
| <bdi>קו"כ כתיב מילה חדה וקרי תרתין מילין</bdi> | Like the k1→q2 case but in reversed (qk) display order, for use after maqaf (Nehemiah 2:13 only) |
| <bdi>כו"ק קרי שונה מהכתיב בשתי מילים</bdi> | 1-word ketiv, 2-word qere (kq display order) |
| <bdi>קו"כ קרי שונה מהכתיב בשתי מילים</bdi> | 1-word ketiv, 2-word qere in reversed (qk) display order (2 Kgs 18:27, Isa 36:12) |
| <bdi>כו"ק של שתי מילים בהערה אחת</bdi> | 2-word ketiv, 2-atom qere |
| <bdi>כו"ק של שלוש מילים בהערה אחת</bdi> | 3-word ketiv, 3-atom qere (2 Samuel 21:12) |

Example (Job 38:1):

```json
{
  "tmpl_name": "מ:כו\"ק מיוחד",
  "tmpl_params": {
    "1": "מנהסערה",
    "2": ["מִ֥ן", {"tmpl_name": "מ:פסק"}, "הַסְּעָרָ֗ה"],
    "סוג": "כו\"ק כתיב מילה חדה וקרי תרתין מילין"
  }
}
```

Here the ketiv "מנהסערה" (one word) is read as "מִ֥ן הַסְּעָרָ֗ה" (two words).

### Targeted scroll-difference note — `מ:הערה-2`

The plain format has `מ:הערה` (a scroll-difference footnote) which is
"non-targeted": it carries the footnote text but does not explicitly
identify which word the note applies to. The plus format adds
`מ:הערה-2`, a "targeted" version that wraps the target word:

```json
{
  "tmpl_name": "מ:הערה-2",
  "tmpl_params": {
    "1": "מִנְּשֹֽׂא",
    "2": "בספרי ספרד ואשכנז מִנְּשֽׂוֹא",
    "3": "אאא*"
  }
}
```

Arguments:
1. The target word (the word the note applies to)
2. The footnote text (the scroll-difference description)
3. Mark position: `"אאא*"` means the note marker (star) comes after
   the target; `"*אאא"` means it comes before (only Deut 22:6)

**The `מ:הערה` template is retained alongside `מ:הערה-2`.** The plus
format redundantly keeps both representations. This is by design:

- The `מ:הערה` template is a faithful representation of what is in the
  upstream Wikisource wikitext. Removing it would lose that fidelity.
- Some downstream consumers use the `מ:הערה-2` template only to extract
  the target word and use the `מ:הערה` template separately to extract
  the footnote text as a standalone annotation. Removing the `מ:הערה`
  template would break those consumers.
- In one verse (Deut 11:21), the two templates are not adjacent: sof
  pasuq is sandwiched between them. The `מ:הערה` template appears after
  sof pasuq (due to Wikisource transclusion needs), but the `מ:הערה-2`
  template correctly excludes sof pasuq from its target. This
  structural divergence means one cannot be trivially derived from the
  other in all cases.

Param 2 of the `מ:הערה-2` template always equals param 1 of the
accompanying `מ:הערה` template. The `מ:הערה-2` template often appears
nested as param 1 of a `נוסח` (documentation note), with the `מ:הערה`
template appearing as a sibling immediately after the `נוסח`:

```json
[
  "וַיֹּ֥אמֶר קַ֖יִן אֶל־יְהֹוָ֑ה גָּד֥וֹל עֲוֺנִ֖י ",
  {
    "tmpl_name": "נוסח",
    "tmpl_params": {
      "1": {
        "tmpl_name": "מ:הערה-2",
        "tmpl_params": {
          "1": "מִנְּשֹֽׂא",
          "2": "בספרי ספרד ואשכנז מִנְּשֽׂוֹא",
          "3": "אאא*"
        }
      },
      "2": "=commentary text..."
    }
  },
  {
    "tmpl_name": "מ:הערה",
    "tmpl_params": {
      "1": "בספרי ספרד ואשכנז מִנְּשֽׂוֹא",
      "שם": "בספרי ספרד ואשכנז מִנְּשֽׂוֹא"
    }
  },
  "׃"
]
```

### Dual-trope text — `מ:כפול`

This template encodes a dually-accented span of text and its corresponding
singly-accented "strands." Used in three sections with dual cantillation:
the two Decalogues (Exodus 20, Deuteronomy 5) and the Saga of Reuben
(Genesis 35:22).

```json
{
  "tmpl_name": "מ:כפול",
  "tmpl_params": {
    "כפול": "...text with two accents on some words...",
    "א": "...strand 1 (singly-accented)...",
    "ב": "...strand 2 (singly-accented)..."
  }
}
```

<!-- ltr -->

Named parameters:
- Param `כפול` — the text with dual accents (as found in the great codexes)
- Param `א` — first singly-accented strand (for Reuben: פשוטה cantillation;
  for Decalogues: תחתון cantillation)
- Param `ב` — second singly-accented strand (for Reuben: מדרשית cantillation;
  for Decalogues: עליון cantillation)

## Common templates (shared with plain)

These templates appear in both formats. In plus they use `tmpl_name`/`tmpl_params`
format:

| Template | Purpose |
|----------|---------|
| <bdi>מ:לגרמיה-2</bdi> | _Legarmeh_ (as distinct from _paseq_) |
| <bdi>מ:פסוק</bdi> | Verse label |
| <bdi>מ:פסק</bdi> | _Paseq_ (as distinct from _legarmeh_) |
| <bdi>מ:דחי</bdi> | Deḥi variation: without stress helper and with stress helper |
| <bdi>מ:צינור</bdi> | Tsinnor variation: without stress helper and with stress helper |
| <bdi>מ:קמץ</bdi> | Qamats variation: A qamats that is qatan in ד is gadol in ס |
| <bdi>מ:מקף אפור</bdi> | Gray (implicit) maqaf |
| <bdi>נוסח</bdi> | Documentation note |
| <bdi>קו"כ</bdi> | Standard ketiv-qere |
| <bdi>קו"כ</bdi> | Post-maqaf ketiv-qere |
| <bdi>מ:כו"ק מיוחד</bdi> | Special ketiv-qere (9 subtypes via `סוג=`; see [section above](#special-ketiv-qere-template-מכוק-מיוחד)) |
| <bdi>מ:קו"כ-אם-2</bdi> | Trivial ketiv-qere |
| <bdi>פפ, סס</bdi>, etc. | Parashah petuchah / setumah |
| <bdi>ר0–ר4</bdi> | Poetic spacing |

## Templates not in plus (removed from plain)

The following plain-format features are absent in plus:

- `{"custom_tag": "noinclude"}` / `{"custom_tag": "/noinclude"}` — custom XML tags
- `{"tmpl": [...]}` — parsed template trees (replaced by `tmpl_name`/`tmpl_params`)
- `{"stmpl": "..."}` — stringified templates (replaced by `tmpl_name`/`tmpl_params`)
- `"0"` and `"תתת"` pseudo-verses
- `"//"` Wikitext line breaks in D column
- <bdi>`גלגל-2`</bdi> — galgal accent annotation (handled differently in plus)
