# MAM-parsed
 
This Git repository contains
[Miqra According to the Masorah](https://en.wikisource.org/wiki/User:Dovi/Miqra_according_to_the_Masorah)
in two parsed formats: "plain" and "plus."
<!-- No non-Dovi equivalent currently exists for this page on en.wikisource.org. -->

Each format contains a JSON file for each of the 24 books of the Miqra.

The source of this data is the
[MAM Google Sheet](https://purl.org/mam/google-sheet#gid=920165745).

Each JSON file represents its corresponding book in a format that is easier to read than the format of the Google Sheet.
(It is easier for a *program* to read, that is. It is not very human-readable.)

The format of the JSON files is easier to read because it is a *parsed* format.
The cells of the C and E columns of the tabs of the Google Sheet are just big Wikitext strings,
including Wikitext templates, e.g. `{{f|a|b|c}}`.
In contrast, the JSON files represent the C and E column data as
parse trees that "know" about the Wikitext template format.

The contents of the "plain" format files is quite close to
the contents of the corresponding tabs of the Google Sheet.
In contrast, the contents of the "plus" format files diverge
from the Google Sheet in the following ways:

* Compared to the Google Sheet, the "plus" format adds:
    * A `good_ending` key to the `book39` header.
    * A targeted version of each מ:הערה template call.
    * A template marking each word with special letters.
* Compared to the Google Sheet, the "plus" format removes:
    * custom XML tags
    * 0 (zero) and תתת (triple-tav) pseudo-verses

For detailed documentation of the file structures, see:

* [Reading MAM-parsed plain](https://bdenckla.github.io/MAM-parsed/plain/html/mpplain.html) — structure reference for the "plain" format
* [Reading MAM-parsed plus](https://bdenckla.github.io/MAM-parsed/plus/html/mpplus.html) — structure reference for the "plus" format

This Git repository also contains a toy sample application
[`main_tmpl_survey_toy.py`](py-examples/main_tmpl_survey_toy.py),
giving some sense of how the JSON files might be used.
It writes its output to [`py-examples-out/tmpl_survey_toy.json`](py-examples-out/tmpl_survey_toy.json).

The format of these JSON files is not yet stable. I.e. if you write an application
based on their format, be aware that their format is still subject to change at this time.

Other versions/formats of MAM (each with their tradeoffs) include:

* [MAM-simple](https://github.com/bdenckla/MAM-simple)
* [MAM for Sefaria](https://github.com/bdenckla/MAM-for-Sefaria)

Questions? Email maintainer@miqra.simplelogin.com.
