# MAM-parsed
 
This Git repository contains MAM (Miqra According to the Masorah) in a parsed format.

It contains a JSON file for each of the 6 main tabs of the MAM Google Sheet.

Each JSON file represents its corresponding tab in an easier-to-read format.

(It is easier for a *program* to read, that is. It is not very human-readable.)

The format of the JSON files is easier to read because it is *parsed*.

The cells of the C and E columns of each tab are just big Wikitext strings,
including Wikitext templates.

In contrast, the JSON files represent the C and E column data as
parse trees that "know" about the Wikitext template format, e.g. {{f|a|b|c}}.

This Git repository also contains a toy sample application giving some sense of how
the JSON files might be used.

The format of these JSON files is not yet stable. I.e. if you write an application
based on their format, be aware that their format is still subject to change at this time.
