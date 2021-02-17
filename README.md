# avatar
AVATAR: Bentley A/V dAtabase To ARchivesspace (for `<dsc>` elements)

## Description
Add ArchivesSpace <dsc> elements from data output from the A/V Database.

## Input

This CLI, which supports the Bentley's A/V Database --> ArchivesSpace workflow, assumes a spreadsheet with the following columns as an input:

- resource id (not from A/V Database)*
- object id (not from A/V Database)*
- Type of obj id (not from A/V Database)* <-- Item | Parent | Grandparent
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

You will need to do a little cleanup on the source .XLSX file. Convert it to a UTF-8 encoded CSV, and clean up any character encoding issues, particularly in AUDIO_ITEMCHAR::TapeSpeed.

## Crosswalk: A/V Database --> ArchivesSpace

[Link to Crosswalk: A/V Database --> ArchivesSpace](https://docs.google.com/document/d/1gZbOyguT6j5rvArEEjrihcbUaPzM1bJ62SbbPd8pMCc/edit?usp=sharing)

## Configuration File

In order to authenticate to ArchivesSpace and use the ArchivesSpace API, supply a "config.ini" file in the "avatar" directory that looks like this:

```
[ArchivesSpace]
BaseURL = 
User = 
Password = 
RepositoryID = 
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