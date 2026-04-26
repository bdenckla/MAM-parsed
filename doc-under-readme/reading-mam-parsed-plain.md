# Reading MAM-parsed plain JSON

> **⚠ Note:** This documentation was AI-generated and is known to contain inaccuracies, but it is a lot better than no documentation.

This document describes the structure of the **plain** format JSON files
in the MAM-parsed repository.

Each JSON file corresponds to one of the 24 books of the Miqra.
The "plain" format closely mirrors the contents of the
[MAM Google Sheet](https://docs.google.com/spreadsheets/d/1mkQyj6by1AtBUabpbaxaZq9Z2X3pX8ZpwG91ZCSOEYs/edit#gid=920165745),
with the Wikitext in columns C and E parsed into structured objects.

Besides Unicode text (letters, niqqud, and accents), the data contains
**templates** — functions, often with parameters, representing visible
features in the masoretic text or concepts related to its presentation.
These features require documentation and/or formatting beyond simple
Unicode characters. Many template names begin with `מ:` (short for
`מקרא`), indicating they are specific to the Miqra al pi ha-Masorah
project. Any implementation consuming this data must decide how to
interpret and apply the templates according to its own needs and goals.

For the "plus" format, which adds and removes certain features,
see [reading-mam-parsed-plus.md](reading-mam-parsed-plus.md).

## File naming

Files are named `{section}{number}-{EnglishName}.json`:

| Prefix | Section | Books |
|--------|---------|-------|
| A1–A5 | Torah | Genesis, Exodus, Leviticus, Numbers, Deuteronomy |
| B1, B2, BA, BC | Former Prophets | Joshua, Judges, Samuel, Kings |
| C1–C3, CA | Latter Prophets | Isaiah, Jeremiah, Ezekiel, The 12 Minor Prophets |
| D1–D3 | Wisdom | Psalms, Proverbs, Job |
| E1–E5 | Five Scrolls | Song of Songs, Ruth, Lamentations, Ecclesiastes, Esther |
| F1, FA, FC | Late Books | Daniel, Ezra-Nehemiah, Chronicles |

When the number is replaced by a letter (`A`, `C`),
the file is a **composite book** containing multiple book39 entries
(e.g. Samuel contains 1 Samuel + 2 Samuel).

## Top-level structure

```json
{
  "header": {
    "book24_names": ["ספר איוב"],
    "sub_book_names": {},
    "chapter_counts": [
      {
        "book24_name": "ספר איוב",
        "sub_book_name": null,
        "chapter_count": 42
      }
    ]
  },
  "book39s": [ ... ]
}
```

| Key | Type | Description |
|-----|------|-------------|
| `header` | object | Metadata: book names, sub-book names, chapter counts |
| `book39s` | array | One element per book39 (sub-book). Usually 1; composite books have 2+ |

### Composite books

For composite books like Samuel, `book39s` has multiple entries:

```json
{
  "header": {
    "book24_names": ["ספר שמואל"],
    "sub_book_names": {"ספר שמואל": ["שמ\"א", "שמ\"ב"]},
    "chapter_counts": [
      {"book24_name": "ספר שמואל", "sub_book_name": "שמ\"א", "chapter_count": 31},
      {"book24_name": "ספר שמואל", "sub_book_name": "שמ\"ב", "chapter_count": 24}
    ]
  },
  "book39s": [
    {"book24_name": "ספר שמואל", "sub_book_name": "שמ\"א", "chapters": {...}},
    {"book24_name": "ספר שמואל", "sub_book_name": "שמ\"ב", "chapters": {...}}
  ]
}
```

## Book39 entry

```json
{
  "book24_name": "ספר איוב",
  "sub_book_name": null,
  "chapters": { ... }
}
```

## Chapter structure

`chapters` is a **dict** keyed by Hebrew-letter chapter names:

```
"א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י",
"יא", "יב", ..., "כ", "כא", ..., "ל", "לא", ..., "מב"
```

These follow standard Hebrew gematria numbering:
- 1–9: א–ט
- 10–19: י, יא–יט
- 15 and 16 use טו and טז (not יה, יו) to avoid spelling divine names
- 20–29: כ, כא–כט
- and so on

Each chapter is also a **dict** keyed by Hebrew-letter verse names,
plus two special pseudo-verse keys:

| Key | Category | Purpose |
|-----|----------|---------|
| `"0"` | Pre-chapter | Wiki navigation templates, page setup |
| `"א"`, `"ב"`, ... | Normal verses | Actual verse data |
| `"תתת"` | Post-chapter | Wiki footer templates, end-of-chapter markup |

## Verse (pseudo-verse) structure

Each verse is a **3-element array** `[D, CP, EP]`, named after the corresponding
columns of the Google Sheet:

```json
["<D column data>", "<C column parsed>", "<E column parsed>"]
```

| Index | Name | Google Sheet column | Content |
|-------|------|---------------------|---------|
| 0 | D | D (section markers) | Parashah break type or `"__"` for continuation |
| 1 | CP | C (verse reference) | Parsed `מ:פסוק` template identifying the verse |
| 2 | EP | E (verse text) | Parsed verse text with inline templates |

### D column (index 0): Section markers

The D column indicates parashah breaks and other section boundaries:

| Value | Meaning |
|-------|---------|
| `["__"]` | No break (continuation from previous verse) |
| `["//", {"stmpl": "פפ"}, "//"]` | **Parashah petuchah** (open paragraph) — blank line separates the end of the previous parashah from the start of the next |
| `["//", {"stmpl": "סס"}, "//"]` | **Parashah setumah** (closed paragraph) — next parashah begins on a new indented line |
| `[{"stmpl": "מ:ספר חדש\|..."}]` | **New book marker** — marks the start of one of the 24 books with defined spacing; parameter is the book name. Not used for second halves of two-part books (2 Samuel, 2 Kings, Nehemiah, 2 Chronicles) or individual Minor Prophets after Hosea |
| `[{"stmpl": "מ:אין פרשה בתחילת פרק"}]` | **No parashah at chapter start** — tags chapters that don't begin with a visible parashah, so appropriate spacing can be added when text is presented sequentially |

Additional parashah-related templates that may appear:

| Template | Meaning |
|----------|---------|
| `פפפ` | Open parashah starting immediately on the next line (no blank line) |
| `ססס` | Closed parashah inline — blank spaces mid-line with text before and after |
| `סס2` | Narrow closed parashah — smaller indentation for narrow-column layouts (e.g. Ten Commandments charts) |
| `פסקא באמצע פסוק` | Parashah division within a verse; first param is the parashah template (`פפ`/`סס`), optional second param gives the verse location |
| `מ:רווח בתרי עשר` | Spacing between Minor Prophets; parameter is the prophet's name |
| `מ:רווח לספר בתהלים` | Spacing between the 5 "books" of Psalms (at Psalms 1, 42, 73, 90, 107); parameter is the book name |

The `"//"` strings are Wikitext line breaks from the Google Sheet.

### CP column (index 1): Verse reference

Contains a `מ:פסוק` template identifying the verse:

```json
[{"stmpl": "מ:פסוק|איוב|א|ב"}]
```

This is equivalent to the Wikitext `{{מ:פסוק|איוב|א|ב}}`.
The three required parameters are: book name, chapter number, and verse number
(all in Hebrew letters). Optional named parameters include `סדר=` (seder number)
and `עלייה=` (Torah aliyah identification). All numbering follows Koren
(the only exception being initial verses of the Ten Commandments).
Note: Ovadiah is spelled `עובדיה` in this template but `עבדיה` in column A.

Empty `[]` for pseudo-verses.

### EP column (index 2): Verse text

Contains the actual verse text as a mixed array of:
- **Strings**: Hebrew text with cantillation marks
- **Template objects**: Inline markup (see below)

Example (Job 1:1):

```json
[
  "אִ֛ישׁ הָיָ֥ה בְאֶֽרֶץ־ע֖וּץ אִיּ֣וֹב שְׁמ֑וֹ וְהָיָ֣ה",
  {"stmpl": "מ:לגרמיה-2"},
  " הָאִ֣ישׁ הַה֗וּא תָּ֧ם וְיָשָׁ֛ר וִירֵ֥א אֱלֹהִ֖ים וְסָ֥ר מֵרָֽע׃"
]
```

To extract plain text, concatenate the string elements and extract the
first argument of relevant templates (e.g. `קו"כ`, `נוסח`).

## Template (atom) formats in plain

The plain format uses three kinds of template atom:

### 1. Stringified template (`stmpl`)

Most templates appear as a pipe-delimited string:

```json
{"stmpl": "מ:פסוק|איוב|א|ב"}
```

This represents the Wikitext `{{מ:פסוק|איוב|א|ב}}`.
The first segment (before `|`) is the template name;
remaining segments are positional arguments.

### 2. Parsed template tree (`tmpl`)

Some complex templates (mainly in pseudo-verses) appear as parse trees:

```json
{
  "tmpl": [
    ["#בלי קטע:", {"stmpl": "שם הדף המלא"}],
    ["סימן"]
  ]
}
```

The first sub-array is the template name (possibly containing nested templates);
subsequent sub-arrays are the arguments.

### 3. Custom XML tag (`custom_tag`)

Wikitext custom XML tags that appear in pseudo-verses:

```json
{"custom_tag": "noinclude"}
{"custom_tag": "/noinclude"}
```

## Common templates in the EP (verse text) column

For authoritative English and Hebrew descriptions of every template, see the
[Templates tab](https://docs.google.com/spreadsheets/d/1mkQyj6by1AtBUabpbaxaZq9Z2X3pX8ZpwG91ZCSOEYs/edit?gid=1670945398#gid=1670945398)
of the MAM Google Sheet.

The templates are organized below by category.

### Documentation template (`נוסח`)

The most extensively used template. Its first parameter is the "target" — the
exact text appearing in the edition. The second parameter contains notes
documenting anomalous forms, variant readings, uncertain readings, and other
data relevant to the target. The template is designed not to interfere with
how the target text appears to the reader; it only marks notable, unusual,
or questionable elements and attaches documentation to them.

```json
{"stmpl": "נוסח|וּבֵרְﬞכ֥וּ|2=א=וּבֵרֲכ֥וּ (חטף)"}
```

### Ketiv-qere templates

| Template | Purpose |
|----------|---------|
| `כו"ק` | **Standard ketiv-qere.** Param 1 = unpointed ketiv, param 2 = pointed qere. Displays ketiv (gray) then qere (regular color) |
| `קו"כ` | **Reversed ketiv-qere.** Same parameters as `כו"ק` but displays qere *before* ketiv. Used when the pair follows a maqaf, for better appearance |
| `קו"כ-אם` | **Trivial ketiv-qere (legacy name).** For cases where the qere differs only in spelling (אֵם קריאה). No ketiv/qere pair is displayed; the vocalized ketiv is shown normally. Param 1 = pointed ketiv, param 2 = a structured note describing the pointed qere (e.g. `ל-קרי=…`, `א-קרי=…`, or similar). **This name is replaced by `מ:קו"כ-אם-2` in current Wikisource data** (see below) |
| `מ:קו"כ-אם-2` | **Trivial ketiv-qere (current name).** Same semantic as `קו"כ-אם` but with explicit parameters. Param 1 = pointed ketiv, param 2 = unpointed ketiv, param 3 = pointed qere, optional `מקורות=` = source indicator, optional `סוג=` = category label |
| `כתיב ולא קרי` | **Written but not read.** Single parameter = the ketiv, shown in gray within parentheses. E.g. `(אם)` in Ruth 3:12 |
| `קרי ולא כתיב` | **Read but not written.** Single parameter = the qere, shown normally within square brackets. E.g. `[אֵלַ֔י]` in Ruth 3:17 |
| `מ:קו"כ קרי שונה מהכתיב בשתי מילים` | **Two-word qere (special).** For 2 Kings 18:27 and Isaiah 36:12 where one ketiv maps to two qere words and the first qere appears in brackets. Three params: ketiv, first qere (bracketed), second qere |

Current values observed for optional `סוג=` in `מ:קו"כ-אם-2` are:

- `אל"ף מיותרת`
- `כתיב ה"א בסיומת של חולם`
- `כתיב הוא קרי היא`
- `כתיב חסר יו"ד בסיומת של קמץ ואחריו וי"ו`
- `כתיב נער קרי נערה`

Example of standard ketiv-qere:

```json
{"stmpl": "קו\"כ|את|אַ֠תָּ֠ה"}
```

### Special letter templates

| Template | Purpose |
|----------|---------|
| `מ:אות-ג` | **Large letter.** Marks a masoretically large letter. Parameter is the pointed letter (occurs within a word). Often wrapped in `נוסח` since traditions vary |
| `מ:אות-ק` | **Small letter.** Marks a masoretically small letter. Parameter is the pointed letter |
| `מ:אות תלויה` | **Suspended (hung) letter.** Appears raised in the text. Parameter is the pointed letter |
| `מ:אות מנוקדת` | **Dotted letter/word.** Marks words with masoretic dots above/below (dots are Unicode). Parameter is the dotted word |
| `מ:נו"ן הפוכה` | **Reversed nun.** The inverted nun mark (Unicode character) |

### Accent and cantillation templates

| Template | Purpose |
|----------|---------|
| `מ:לגרמיה-2` | **Legarmeih.** The vertical line `׀` as legarmeih (part of the word's cantillation). Shown close to the preceding word with thin space, in bold. Shares Unicode with paseq but differs in function |
| `מ:פסק` | **Paseq.** The vertical line `׀` as a separator warning not to conflate two words. Shown equidistant between words, small gray font. No parameters |
| `מ:מקף אפור` | **Gray maqaf.** Gray hyphen between oleh-ve-yored words in 50 verses of Psalms, Proverbs, and Job. No parameters |
| `מ:דחי` | **Dechik** accent annotation |
| `מ:צינור` | **Tsinor** accent annotation |
| `גלגל-2` | **Galgal accent** (3 poetic books). Same Unicode character as yeraḥ ben yomo but distinguished as in the Aleppo Codex |
| `ירח בן יומו` | **Yeraḥ ben yomo accent** (21 books). Same Unicode character as galgal. No parameters |
| `אתנח הפוך` | **Etnaḥ haphukh** (3 poetic books). Similar to but distinct from galgal in the Aleppo Codex; later codices merged them. No parameters |
| `מ:קמץ` | **Qamats qatan.** Named params: `ד=` (theoretical grammar, default) and `ס=` (Sephardic tradition, which less often voices qamats qatan in certain forms) |

### Jerusalem spelling

| Template | Purpose |
|----------|---------|
| `מ:ירושלם` | Handles the masoretic spelling of Jerusalem without yod. Two params (vowel and accent of lamed); automatically provides ḥiriq for the missing yod with CGJ for proper display |
| `מ:ירושלמה` | Like `מ:ירושלם` but for the directional form "to Jerusalem" (4 cases: 1 Kgs 10:2, 2 Kgs 9:28, Isa 36:2, Ezk 8:3). Uses sheva instead of ḥiriq |

### Poetic form templates (ספרי אמ"ת)

| Template | Purpose |
|----------|---------|
| `ר1` | Following stich on its own line, **one** indent. In 2 cases (Ps 70, 108) represents a closed parashah |
| `ר2` | Following stich on its own line, **two** indents |
| `ר3` | Following stich at line start, **no** indent |
| `ר4` | New verse at line start, **no** indent |
| `ר0` | Extra division point when a verse has an odd number of stiches, for even-column display |
| `פרשה-מרכז` | **Centered title.** For "titles" in Job and Proverbs (not found elsewhere). Parameter is the title text |

All poetic formatting can be removed by treating `ר0`–`ר4` as simple word spaces.

### Footnote template

| Template | Purpose |
|----------|---------|
| `מ:הערה` | **Scroll-difference footnote** (Torah and Esther only). Footnote markers appear within the text itself. Parameter is the footnote text |

### Other templates

| Template | Purpose |
|----------|---------|
| `פפ` / `סס` | Parashah petuchah / setumah (primarily in D column) |
| `מ:סיום בטוב` | **Good ending.** Repeats the penultimate verse so public reading ends positively. Used at the end of Lamentations, Ecclesiastes, Isaiah, and Malachi |
| `מ:טעם ומתג באות אחת` | Normalization-robust meteg for 10 cases where a below-accent and meteg share one letter |
| `מ:גרש ותלישא גדולה` | Combined geresh + telisha gedolah (2 words, 3 uses). No parameters |
| `מ:גרשיים ותלישא גדולה` | Combined gershayim + telisha gedolah (3 words, 4 uses). No parameters |

## Extracting plain text from verses

To extract the verse text for programmatic use,
iterate over the EP column (index 2) and handle each atom:

```python
import json
from pathlib import Path

book = json.loads(Path('plain/D3-Job.json').read_text('utf-8'))
b39 = book['book39s'][0]
chapters = b39['chapters']

def extract_text(ep_column):
    """Extract plain text from EP column atoms."""
    parts = []
    for atom in ep_column:
        if isinstance(atom, str):
            parts.append(atom)
        elif isinstance(atom, dict):
            stmpl = atom.get('stmpl', '')
            name = stmpl.split('|')[0] if '|' in stmpl else stmpl
            args = stmpl.split('|')[1:] if '|' in stmpl else []
            if name in ('קו"כ', 'קו"כ-אם', 'מ:קו"כ-אם-2'):
                # Use qere (2nd arg) for reading; for קו"כ-אם / מ:קו"כ-אם-2
                # (matres lectionis kq) the 1st arg is the displayed ketiv.
                if len(args) >= 2:
                    parts.append(args[1])
            elif name == 'נוסח':
                # Use primary text (1st arg)
                if args:
                    parts.append(args[0])
            elif name == 'גלגל-2':
                if args:
                    parts.append(args[0])
            # Skip formatting-only templates (ר0–ר4, מ:לגרמיה-2, etc.)
    return ''.join(parts).strip()

# Print Job 1:1
ch1 = chapters['א']
ep = ch1['א'][2]  # [D, CP, EP] → EP
print(extract_text(ep))
```

## Pseudo-verses (0 and תתת)

The `"0"` and `"תתת"` keys are **pseudo-verses** that contain
Wiki-specific navigation and formatting markup, not biblical text.
They can generally be skipped when extracting verse content.

- `"0"`: Contains `noinclude` tags, navigation templates, margin settings
- `"תתת"`: Contains end-of-chapter markers, unnumbered-verse section

For the template survey example showing how to categorize pseudo-verses
vs. normal verses, see `template-survey-example.py` in the repo root.
