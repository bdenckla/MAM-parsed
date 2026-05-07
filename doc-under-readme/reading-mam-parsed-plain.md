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

File names start with a two-character code identifying the book (in the "24 books" sense).
The first character (`sec_char`), A through F, indicates which of the six sections of Tanakh the book is in.
The second character (`book24_char`), a digit 1 through 5 or an uppercase letter A through C, indicates the book within that section.

Files are named `{sec_char}{book24_char}-{EnglishName}.json`:

| Prefix | Section | Books |
|--------|---------|-------|
| A1–A5 | Torah | Genesis, Exodus, Leviticus, Numbers, Deuteronomy |
| B1, B2, BA, BC | Former Prophets | Joshua, Judges, Samuel, Kings |
| C1–C3, CA | Latter Prophets | Isaiah, Jeremiah, Ezekiel, The 12 Minor Prophets |
| D1–D3 | Wisdom | Psalms, Proverbs, Job |
| E1–E5 | Five Scrolls | Song of Songs, Ruth, Lamentations, Ecclesiastes, Esther |
| F1, FA, FC | Late Books | Daniel, Ezra-Nehemiah, Chronicles |

When `book24_char` is a letter (`A`, `C`),
the file is a **composite book** containing multiple sub-books
(e.g. Samuel contains 1 Samuel + 2 Samuel).
(Sub-books are books in the "39 books" sense.)

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
  "book39s": []
}
```

<!-- ltr -->

Key | Type | Description
--- | ---- | -----------
`header` | object | Metadata: book names, sub-book names, chapter counts.
`book39s` | array | One element per book39 (sub-book).

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
    {"book24_name": "ספר שמואל", "sub_book_name": "שמ\"א", "chapters": {}},
    {"book24_name": "ספר שמואל", "sub_book_name": "שמ\"ב", "chapters": {}}
  ]
}
```

## Book39 entry

```json
{
  "book24_name": "ספר איוב",
  "sub_book_name": null,
  "chapters": {}
}
```

<!-- ltr -->

## Chapter structure

The `chapters` dict is keyed as follows:

| Key | Category | Purpose |
|-----|----------|---------|
| `"0"` | Pre-chapter | Wiki navigation templates, page setup |
| Hebrew numerals | Normal verses | Actual verse data |
| <bdi>`"תתת"`</bdi> | Post-chapter | Wiki footer templates, end-of-chapter markup |

The keys for normal verses are Hebrew numerals
conforming to the system that 
uses טו and טז for 15 and 16.
(This avoids the _yod-he_ and _yod-vav_ letter-pairs
that could be associated with the divine name.)

## Verse (pseudo-verse) structure

Each verse is a **3-element array** corresponding to the D, C, and E
columns of the Google Sheet.
(This ordering rather than C, D, E made more sense in this context.)

|      | Content
| ---- | -------
| D    | Verse label (`מ:פסוק` template): book name, chapter number, verse number, etc. |
| C    | Verse separator: parashah break or `"__"` for a plain space |
| E    | Verse text with inline templates |

### Index 0 (Google column D): Verse label

The context at index 0 is empty `[]` for pseudo-verses.
For normal verses, it is a list containing exactly one element:
The `מ:פסוק` template labeling the verse, e.g. for Job 1:2:

```json
[{"stmpl": "מ:פסוק|איוב|א|ב"}]
```

This is equivalent to the Wikitext `{{מ:פסוק|איוב|א|ב}}`.
The three required parameters are:
book name (Hebrew alphabet string),
chapter number (Hebrew numeral), and
verse number (Hebrew numeral).
Optional named parameters include <bdi>`סדר=`</bdi> (seder number)
and <bdi>`עלייה=`</bdi> (Torah aliyah identification).
Note: Ovadiah is spelled `עובדיה` in this template but `עבדיה` in column A.


### Index 1 (Google column C): Verse separator

The contents at index 1 indicates how this verse is separated from the verse that precedes it.
Double underscoe (`"__"`) is by var the most common value here, indicating merely a plain space
separating this verse from the verse that precedes it. More interesting values include the following:

| Template | Meaning |
|-------|---------|
| <bdi>`פפ`</bdi> | **Parashah petuchah** (open paragraph) |
| <bdi>`סס`</bdi> | **Parashah setumah** (closed paragraph) |
| <bdi>`מ:ספר חדש`</bdi> | **New book marker** — marks the start of one of the 24 books with defined spacing; parameter is the book name. Not used for second halves of two-part books (2 Samuel, 2 Kings, Nehemiah, 2 Chronicles) or individual Minor Prophets after Hosea |
| <bdi>`מ:אין פרשה בתחילת פרק`</bdi> | **No parashah at chapter start** — tags chapters that don't begin with a visible parashah, so appropriate spacing can be added when text is presented sequentially |

Additional parashah-related templates that may appear:

| Template | Meaning |
|----------|---------|
| <bdi>`פפפ`</bdi> | Open parashah starting immediately on the next line (no blank line) |
| <bdi>`ססס`</bdi> | Closed parashah inline — blank spaces mid-line with text before and after |
| <bdi>`סס2`</bdi> | Narrow closed parashah |
| <bdi>`פסקא באמצע פסוק`</bdi> | Parashah division within a verse |
| <bdi>`מ:רווח בתרי עשר`</bdi> | Spacing between Minor Prophets |
| <bdi>`מ:רווח לספר בתהלים`</bdi> | Spacing between the 5 "books" of Psalms (at Psalms 1, 42, 73, 90, 107) |

The `"//"` strings sometimes sprinkled in Index 1 are Wikitext line breaks from the Google Sheet.

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

## Template objects in plain

The plain format uses three kinds of template objects:

### 1. Stringified template (`stmpl`)

Many templates are simple enough and short enough appear as a pipe-delimited string:

```json
{"stmpl": "מ:פסוק|איוב|א|ב"}
```

This represents the Wikitext `{{מ:פסוק|איוב|א|ב}}`.
The first segment (before `|`) is the template name;
remaining segments are positional arguments.

### 2. Parsed template tree (`tmpl`)

Longer and/or more complex templates appear as parse trees:

```json
{
  "tmpl": [
    ["#בלי קטע:", {"stmpl": "שם הדף המלא"}],
    ["סימן"]
  ]
}
```

The first sub-array is the template name.
Subsequent sub-arrays are the arguments.
The arguments may contain nested template "calls".

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

Its first parameter is the "target" — what is being documented.
The second parameter contains the documentation.
Examples of documentation include
anomalous forms,
variant readings,
uncertain readings, and
other information relevant to the target.

```json
{"stmpl": "נוסח|וּבֵרְﬞכ֥וּ|2=א=וּבֵרֲכ֥וּ (חטף)"}
```

### Ketiv-qere templates

| Template | Purpose |
|----------|---------|
| <bdi>`כו"ק`</bdi> | **standard ketiv-qere.** Param 1 = unpointed ketiv, param 2 = pointed qere. |
| <bdi>`קו"כ`</bdi> | **post-maqaf ketiv-qere.** Same parameters as `כו"ק` but used when the pair follows a maqaf. Some editions choose to display pairs like this with the qere *before* ketiv. |
| <bdi>`מ:קו"כ-אם-2`</bdi> | **trivial ketiv-qere.** For cases where the difference between the ketiv and the qere is deemed trivial. Some editions choose to display only the vocalized ketiv in such cases. Param 1 = pointed ketiv, param 2 = unpointed ketiv, param 3 = pointed qere, optional `מקורות=` = source indicator, optional `סוג=` = category label. |
| <bdi>`כתיב ולא קרי`</bdi> | **ketiv without qere.** Single parameter = the ketiv, shown in gray within parentheses. E.g. `(אם)` in Ruth 3:12 |
| <bdi>`קרי ולא כתיב`</bdi> | **qere without ketiv.** Single parameter = the qere, shown normally within square brackets. E.g. `[אֵלַ֔י]` in Ruth 3:17 |
| <bdi>`מ:כו"ק מיוחד`</bdi> | **special ketiv-qere.** The required `סוג=` named parameter identifies the subtype. See the [plus format documentation](reading-mam-parsed-plus.md) for the full subtype list. |

Current values observed for optional `סוג=` in `מ:קו"כ-אם-2` are:

- `אל"ף נחה באמצע תיבה ולא נקראת`
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
| <bdi>`מ:אות-ג`</bdi> | **Large letter.** Marks a masoretically large letter. Parameter is the pointed letter (occurs within a word). Often wrapped in `נוסח` since traditions vary |
| <bdi>`מ:אות-ק`</bdi> | **Small letter.** Marks a masoretically small letter. Parameter is the pointed letter |
| <bdi>`מ:אות תלויה`</bdi> | **Suspended (hung) letter.** Appears raised in the text. Parameter is the pointed letter |
| <bdi>`מ:אות מנוקדת`</bdi> | **Dotted letter/word.** Marks words with masoretic dots above/below (dots are Unicode). Parameter is the dotted word |
| <bdi>`מ:נו"ן הפוכה`</bdi> | **Reversed nun.** The inverted nun mark (Unicode character) |

### Accent and cantillation templates

| Template | Purpose |
|----------|---------|
| <bdi>`מ:לגרמיה-2`</bdi> | **Legarmeh.** The vertical line `׀` as legarmeh (part of the word's cantillation).  Shares Unicode with paseq but differs in function |
| <bdi>`מ:פסק`</bdi> | **Paseq.** The vertical line `׀` as _paseq_ in the narrow sense, i.e. _paseq_ as distinct from _legarmeh_. |
| <bdi>`מ:מקף אפור`</bdi> | **Gray maqaf.** A _maqaf_ that is only implicit in the manuscript. Appears only in poetic verses. |
| <bdi>`מ:דחי`</bdi> | **Deḥi variation.** Presents both stress-helped and non-stress-helped versions of a word. |
| <bdi>`מ:צינור`</bdi> | **Tsinnor variation.** Presents both stress-helped and non-stress-helped versions of a word. |
| <bdi>`גלגל-2`</bdi> | **Galgal.** Distinguishes poetic from prose uses of Unicode YERAH BEN YOMO. |
| <bdi>`ירח בן יומו`</bdi> | **Yeraḥ ben yomo.** Distinguishes prose from poetic uses of Unicode YERAH BEN YOMO. |
| <bdi>`אתנח הפוך`</bdi> | **Atnaḥ hafukh.** Helps distinguish this accent from galgal/yeraḥ ben yomo because many fonts do not make this distinction. |
| <bdi>`מ:קמץ`</bdi> | **Qamats variation.** Named params: `ד=` (theoretical/grammatical) and `ס=` (Sephardic tradition, which less often voices qamats qatan in certain forms). |

### Jerusalem spelling

| Template | Purpose |
|----------|---------|
| <bdi>`מ:ירושלם`</bdi> | Handles the masoretic spelling of Jerusalem without yod. Two params (vowel and accent of lamed); automatically provides ḥiriq for the missing yod with CGJ for proper display |
| <bdi>`מ:ירושלמה`</bdi> | Like `מ:ירושלם` but for the directional form "to Jerusalem" (4 cases: 1 Kgs 10:2, 2 Kgs 9:28, Isa 36:2, Ezk 8:3). Uses sheva instead of ḥiriq. |

### Poetic form templates (ספרי אמ"ת)

| Template | Purpose |
|----------|---------|
| <bdi>`ר1`</bdi> | Following stich on its own line, **one** indent. In 2 cases (Ps 70, 108) represents a closed parashah |
| <bdi>`ר2`</bdi> | Following stich on its own line, **two** indents |
| <bdi>`ר3`</bdi> | Following stich at line start, **no** indent |
| <bdi>`ר4`</bdi> | New verse at line start, **no** indent |
| <bdi>`ר0`</bdi> | Extra division point when a verse has an odd number of stiches, for even-column display |
| <bdi>`פרשה-מרכז`</bdi> | **Centered title.** For "titles" in Job and Proverbs (not found elsewhere). Parameter is the title text |

Many editions will choose to skip poetic formatting by treating `ר0`–`ר4` as simple word spaces.

### Footnote template

| Template | Purpose |
|----------|---------|
| <bdi>`מ:הערה`</bdi> | **Scroll-difference footnote** (Torah and Esther only). Footnote markers appear within the text itself. Parameter is the footnote text |

### Other templates

| Template | Purpose |
|----------|---------|
| <bdi>`פפ` / `סס`</bdi> | Parashah petuchah / setumah (primarily in D column) |
| <bdi>`מ:סיום בטוב`</bdi> | **Good ending.** Repeats the penultimate verse so public reading ends positively. Used at the end of Lamentations, Ecclesiastes, Isaiah, and Malachi |
| <bdi>`מ:טעם ומתג באות אחת`</bdi> | Normalization-robust meteg for 10 cases where a below-accent and meteg share one letter |
| <bdi>`מ:גרש ותלישא גדולה`</bdi> | Combined geresh + telisha gedolah (2 words, 3 uses). No parameters |
| <bdi>`מ:גרשיים ותלישא גדולה`</bdi> | Combined gershayim + telisha gedolah (3 words, 4 uses). No parameters |

## Pseudo-verses (0 and תתת)

The `"0"` and `"תתת"` keys are **pseudo-verses** that contain
Wiki-specific navigation and formatting markup, not biblical text.
They can generally be skipped when extracting verse content.

- `"0"`: Contains `noinclude` tags, navigation templates, margin settings
- <bdi>`"תתת"`</bdi>: Contains end-of-chapter markers, unnumbered-verse section
