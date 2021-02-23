# avatar
AVATAR: Bentley A/V dAtabase To ARchivesspace (for `<dsc>` elements)

## Description
Add ArchivesSpace <dsc> elements from data output from the A/V Database.

## Input

This CLI, which supports the Bentley's A/V Database --> ArchivesSpace workflow, assumes a spreadsheet with the following columns as an input:

- resource id (not from A/V Database)*
- object id (not from A/V Database)*
- Type of obj id (not from A/V Database)* <-- Parent | Item | Part
- DigFile Calc*
- AVType::ExtentType*
- AVType::Avtype*
- ItemTitle*
- ItemPartTitle
- ItemDate*
- MiVideoID
- NoteContent*
- AUDIO_ITEMCHAR::Fidleity
- AUDIO_ITEMCHAR::ReelSize
- AUDIO_ITEMCHAR::TapeSpeed
- ItemPolarity
- ItemColor
- ItemSound
- ItemTime*

_Note: Required columns are designated with an asterisk (*)._ 

You will need to do a little cleanup on the source .XLSX file. Convert it to a UTF-8 encoded CSV, and clean up any character encoding issues, particularly fractions in AUDIO_ITEMCHAR::TapeSpeed.

## Basic Logic

First, AVATAR characterizes each row in the spreadsheet to determine:

- whether the corresponding ArchivesSpace archival object is a _parent_, _item_, or _part_ of the row using the "Type of obj id" column;
- whether the row is an _item ONLY_ or and _item with parts_ using the "DigFile Calc column"; and
- whether the row is _audio_ or _moving image_ using the "DigFile Calc" column.

The basic logic for creating or updating archival objects and creating and linking digital objects in ArchivesSpace, is, then:

Expression | Statement
--- | ---
If the corresponding ArchivesSpace archival object is a _parent_ and the row is an _item only_... | ..._create_ a child archival object, _create and link_ a digital object (preservation) to the child archival object, and _create and link_ digital object (access) to the child archival object.
Else if the corresponding ArchivesSpace archival object is an _item_ and the row is an _item only_... | ... _update_ the archival object, _create and link_ a digital object (preservation) to the archival object, and _create and link_ a digital object (access) to the archival object.
Else if the corresponding ArchivesSpace archival object is an _part_ and the row is an _item only_... | NOT APPLICABLE
Else if the corresponding ArchivesSpace archival object is a _parent_ and the row is an _item with parts_... | ..._create_ a child archival object for the _item_, _create and link_ a digital object (preservat) to the child archival object, add a child archival object to the child archival object for the _part_, and _create and link_ a digital object (access) to the child archival object of the child archival object.
Else if the corresponding ArchivesSpace archival object is an _item_ and the row is an _item with parts_... | ..._update_ the archival object for the _item_, _create and link_ a digital object (preservation) to the archival object, add a child archival for the _part_, and _create and link_ a digital object (access) to the child archival object for the _part_.
Else if the corresponding ArchivesSpace archival object is an _part_ and the row is an _item with parts_... | ..._update_ the parent archival object for the _item_, _create and link_ a digital object (preservation) to the parent archival object, update the archival object for the _part_, and _create and link_ a digital object (access) on the archival object.

## Crosswalk: A/V Database --> ArchivesSpace

[Link to Crosswalk: A/V Database --> ArchivesSpace](https://docs.google.com/document/d/1gZbOyguT6j5rvArEEjrihcbUaPzM1bJ62SbbPd8pMCc/edit?usp=sharing)

## Configuration File

In order to authenticate to ArchivesSpace and use the ArchivesSpace API, supply a "config.ini" file in the "avatar" directory that looks like this:

```
[ArchivesSpace]
BaseURL = ''
User = ''
Password = ''
RepositoryID = ''
```

## A Note on Notes and Dates

## Access Restrictions

## Usage

```
usage: avatar.py [-h] [-d /path/to/destination/directory]
                 /path/to/project/csv.csv

Add ArchivesSpace <dsc> elements from data output from the A/V Database.

positional arguments:
  /path/to/project/csv.csv
                        Path to a project CSV

optional arguments:
  -h, --help            show this help message and exit
  -d /path/to/destination/directory, --dst /path/to/destination/directory
                        Path to destination directory for results
```

## Output