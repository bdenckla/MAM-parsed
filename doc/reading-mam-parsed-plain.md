# Reading MAM-parsed plain JSON

> **⚠ Note:** This documentation was AI-generated and is known to contain inaccuracies, but it is a lot better than no documentation.

This document describes the structure of the **plain** format JSON files
in the MAM-parsed repository.

Each JSON file corresponds to one of the 24 books of the Miqra.
The "plain" format closely mirrors the contents of the
[MAM Google Sheet](https://docs.google.com/spreadsheets/d/1mkQyj6by1AtBUabpbaxaZq9Z2X3pX8ZpwG91ZCSOEYs/edit#gid=920165745),
with the Wikitext in columns C and E parsed into structured objects.

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
| `["//", {"stmpl": "פפ"}, "//"]` | Parashah petuchah (open paragraph) |
| `["//", {"stmpl": "סס"}, "//"]` | Parashah setumah (closed paragraph) |
| `[{"stmpl": "מ:ספר חדש\|..."}]` | New book marker |
| `[{"stmpl": "מ:אין פרשה בתחילת פרק"}]` | No parashah at chapter start |

The `"//"` strings are Wikitext line breaks from the Google Sheet.

### CP column (index 1): Verse reference

Contains a `מ:פסוק` template identifying the verse:

```json
[{"stmpl": "מ:פסוק|איוב|א|ב"}]
```

This is equivalent to the Wikitext `{{מ:פסוק|איוב|א|ב}}`.
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

| Template | Purpose | Example |
|----------|---------|---------|
| `מ:לגרמיה-2` | Legarmeih accent marker | `{"stmpl": "מ:לגרמיה-2"}` |
| `קו"כ` | Ketiv-qere | `{"stmpl": "קו\"כ\|את\|אַ֠תָּ֠ה"}` |
| `קו"כ-אם` | Ketiv-qere (conditional) | Similar to קו"כ |
| `נוסח` | Textual variant (nusach) | `{"stmpl": "נוסח\|וּבֵרְﬞכ֥וּ\|2=..."}` |
| `מ:דחי` | Dechik accent annotation | `{"stmpl": "מ:דחי\|word\|variant"}` |
| `מ:פסק` | Pasek mark | `{"stmpl": "מ:פסק"}` |
| `מ:צינור` | Tsinor accent annotation | `{"stmpl": "מ:צינור"}` |
| `מ:קמץ` | Qamats annotation | `{"stmpl": "מ:קמץ"}` |
| `מ:מקף אפור` | Gray maqaf | `{"stmpl": "מ:מקף אפור"}` |
| `מ:אות תלויה` | Suspended letter | `{"stmpl": "מ:אות תלויה\|..."}` |
| `גלגל-2` | Galgal accent annotation | `{"stmpl": "גלגל-2\|word"}` |
| `ר0`–`ר4` | Re'via annotation tiers | `{"stmpl": "ר0"}` |
| `פפ` / `סס` | Parashah petuchah / setumah | In D column |
| `פרשה-מרכז` | Centered parashah marker | `{"stmpl": "פרשה-מרכז"}` |

### Ketiv-qere (`קו"כ`)

The first argument is the ketiv (written form), the second is the qere (read form):

```json
{"stmpl": "קו\"כ|את|אַ֠תָּ֠ה"}
```

### Nusach (variant reading, `נוסח`)

The first argument is the primary text; the second describes the variant:

```json
{"stmpl": "נוסח|וּבֵרְﬞכ֥וּ|2=א=וּבֵרֲכ֥וּ (חטף)"}
```

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
            if name in ('קו"כ', 'קו"כ-אם'):
                # Use qere (2nd arg) for reading
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
