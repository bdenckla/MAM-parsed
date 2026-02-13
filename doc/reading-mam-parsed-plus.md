# Reading MAM-parsed plus JSON

> **⚠ Note:** This documentation was AI-generated and is known to contain inaccuracies, but it is a lot better than no documentation.

This document describes the structure of the **plus** format JSON files
in the MAM-parsed repository.

The plus format shares the same overall structure as the
[plain format](reading-mam-parsed-plain.md) but diverges in several ways.
Read the plain format documentation first for the foundation,
then use this document for the differences.

## Differences from plain at a glance

| Feature | Plain | Plus |
|---------|-------|------|
| Pseudo-verses `"0"` and `"תתת"` | Present | **Removed** |
| Custom XML tags (`noinclude` etc.) | Present | **Removed** |
| Wikitext line breaks (`"//"`) | Present in D column | **Removed** |
| Template representation | `stmpl` (stringified) | `tmpl_name`/`tmpl_args`/`tmpl_params` |
| CP column (verse reference) | Every verse has `מ:פסוק` | Only first verse of chapter |
| `good_ending_plus` | Not present | **Added** (at book39 level) |
| Special letter marking | Not present | **Added** (`מ:אות-מיוחדת-במילה`) |
| Targeted ketiv-qere templates | Generic only | **Added** (e.g. `מ:כו"ק כתיב מילה חדה...`) |

## Top-level structure

Same as plain:

```json
{
  "header": { ... },
  "book39s": [ ... ]
}
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
after the final verse so that public reading ends on a positive note.
The `good_ending_plus` key captures this:

- `null` for most books (including Job)
- For books that have it (Isaiah, Malachi, Lamentations, Ecclesiastes),
  it is an object with:

```json
{
  "last_chapnver": ["סו", "כד"],
  "wikitext_element": {
    "tmpl_name": "נוסח",
    "tmpl_args": [
      {"tmpl_name": "מ:סיום בטוב", "tmpl_args": ["..."]},
      ...
    ]
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

Simplified compared to plain. No `"//"` Wikitext line breaks:

| Value | Meaning |
|-------|---------|
| `["__"]` | No break (continuation) |
| `[{"tmpl_name": "פפ"}]` | Parashah petuchah |
| `[{"tmpl_name": "סס"}]` | Parashah setumah |
| `[{"tmpl_name": "מ:ספר חדש", "tmpl_args": ["איוב"]}]` | New book |
| `[{"tmpl_name": "מ:אין פרשה בתחילת פרק"}]` | No parashah at chapter start |

### CP column (index 1): Verse reference

In plus, only the **first verse of each chapter** has the `מ:פסוק` template.
All other verses have an empty `[]`:

```json
// First verse (א):
[{"tmpl_name": "מ:פסוק", "tmpl_args": ["איוב", "א", "א", "סדר=א"], "tmpl_params": {...}}]

// Subsequent verses (ב, ג, ...):
[]
```

(The verse identity is already encoded in the dict key,
so repeating it in CP is redundant.)

### EP column (index 2): Verse text

Same mixed array of strings and template objects,
but templates use the expanded format (see below).

## Template format in plus

All templates in the plus format use the expanded representation:

```json
{
  "tmpl_name": "קו\"כ",
  "tmpl_args": ["את", "אַ֠תָּ֠ה"],
  "tmpl_params": {
    "1": "את",
    "2": "אַ֠תָּ֠ה"
  }
}
```

| Key | Type | Description |
|-----|------|-------------|
| `tmpl_name` | string | Template name |
| `tmpl_args` | array | Positional arguments (strings, arrays, or nested template objects) |
| `tmpl_params` | object | Named parameters (optional; maps param names to values) |

Contrast with the plain format where the same template would be:

```json
{"stmpl": "קו\"כ|את|אַ֠תָּ֠ה"}
```

### Template arguments can be complex

In the plus format, template arguments can themselves be:
- Strings
- Nested template objects
- Arrays of mixed strings and template objects

Example — a word with a special letter inside a ketiv-qere inside a nusach:

```json
{
  "tmpl_name": "נוסח",
  "tmpl_args": [
    {
      "tmpl_name": "כו\"ק",
      "tmpl_args": [
        {
          "tmpl_name": "מ:אות-מיוחדת-במילה",
          "tmpl_args": [
            ["ו", {"tmpl_name": "מ:אות-ק", "tmpl_args": ["ג"]}, "יש"],
            "וגיש", ".ג..", "ק", "ג/ק"
          ]
        },
        "וְג֣וּשׁ"
      ]
    },
    ["2==commentary text...", ...]
  ]
}
```

## Plus-only templates

### `מ:אות-מיוחדת-במילה` — Special letter marking

Marks a word containing a letter with a special size or form
(large, small, suspended, etc.):

```json
{
  "tmpl_name": "מ:אות-מיוחדת-במילה",
  "tmpl_args": [
    ["שִׁבְ", {"tmpl_name": "מ:אות-ג", "tmpl_args": ["ט֑"]}, "וֹ"],
    "שִׁבְט֑וֹ",
    "..ט.",
    "ג",
    "ט/ג"
  ]
}
```

Arguments:
1. Array showing the word decomposed around the special letter
2. The word as a plain string
3. A dot-mask showing the position of the special letter
4. The size/type code (ג = large, ק = small, etc.)
5. Letter/type summary

### Targeted ketiv-qere templates

The plus format expands generic `קו"כ` cases into specific named templates:

| Template | Meaning |
|----------|---------|
| `מ:כו"ק כתיב מילה חדה וקרי תרתין מילין` | Ketiv is one word, qere is two words |
| `כו"ק` | Standard ketiv-qere (also in plain) |
| `כו"ק-אם` | Conditional ketiv-qere (also in plain) |
| `כו"ק` | Standard (same as plain) |

Example of the targeted template (Job 38:1):

```json
{
  "tmpl_name": "מ:כו\"ק כתיב מילה חדה וקרי תרתין מילין",
  "tmpl_args": [
    "מנהסערה",
    ["מִ֥ן", {"tmpl_name": "מ:פסק"}, "הַסְּעָרָ֗ה"]
  ]
}
```

Here the ketiv "מנהסערה" (one word) is read as "מִ֥ן הַסְּעָרָ֗ה" (two words).

## Common templates (shared with plain)

These templates appear in both formats. In plus they use `tmpl_name`/`tmpl_args`
instead of `stmpl`:

| Template | Purpose |
|----------|---------|
| `מ:לגרמיה-2` | Legarmeih accent marker |
| `מ:פסוק` | Verse reference |
| `מ:פסק` | Pasek mark |
| `מ:דחי` | Dechik accent annotation |
| `מ:צינור` | Tsinor accent annotation |
| `מ:קמץ` | Qamats annotation |
| `מ:מקף אפור` | Gray maqaf |
| `נוסח` | Textual variant |
| `קו"כ` | Ketiv-qere |
| `פפ` / `סס` | Parashah petuchah / setumah |
| `ר0`–`ר4` | Re'via annotation tiers |

## Extracting plain text from plus

```python
import json
from pathlib import Path

book = json.loads(Path('plus/D3-Job.json').read_text('utf-8'))
b39 = book['book39s'][0]
chapters = b39['chapters']

def extract_text(ep_column):
    """Extract plain text from EP column atoms."""
    parts = []
    for atom in ep_column:
        if isinstance(atom, str):
            parts.append(atom)
        elif isinstance(atom, dict):
            name = atom.get('tmpl_name', '')
            args = atom.get('tmpl_args', [])
            if name in ('קו"כ', 'קו"כ-אם'):
                # Use qere (2nd arg)
                if len(args) >= 2 and isinstance(args[1], str):
                    parts.append(args[1])
            elif name == 'נוסח':
                # Use primary text (1st arg)
                if args:
                    first = args[0]
                    if isinstance(first, str):
                        parts.append(first)
                    elif isinstance(first, dict):
                        # Recurse into nested template
                        parts.append(extract_text([first]))
            elif name.startswith('מ:כו"ק'):
                # Targeted kq: 2nd arg is the qere
                if len(args) >= 2:
                    qere = args[1]
                    if isinstance(qere, str):
                        parts.append(qere)
                    elif isinstance(qere, list):
                        parts.append(extract_text(qere))
            elif name == 'מ:אות-מיוחדת-במילה':
                # Use plain word (2nd arg)
                if len(args) >= 2 and isinstance(args[1], str):
                    parts.append(args[1])
            # Skip formatting-only templates (ר0–ר4, מ:לגרמיה-2, etc.)
    return ''.join(parts).strip()

# Print Job 1:1
ch1 = chapters['א']
ep = ch1['א'][2]  # [D, CP, EP] → EP
print(extract_text(ep))
```

## Templates not in plus (removed from plain)

The following plain-format features are absent in plus:

- `{"custom_tag": "noinclude"}` / `{"custom_tag": "/noinclude"}` — custom XML tags
- `{"tmpl": [...]}` — parsed template trees (only in pseudo-verses)
- `{"stmpl": "..."}` — stringified templates (replaced by `tmpl_name`/`tmpl_args`)
- `"0"` and `"תתת"` pseudo-verses
- `"//"` Wikitext line breaks in D column
- `גלגל-2` — galgal accent annotation (handled differently in plus)
