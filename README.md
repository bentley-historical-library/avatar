# avatar
AVATAR: Bentley A/V dAtabase To ARchivesspace (for `<dsc>` elements)

## Description
Add ArchivesSpace <dsc> elements from data in the A/V Database.

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

## Crosswalk: A/V Database --> ArchivesSpace

[Link to Crosswalk: A/V Database --> ArchivesSpace.](https://docs.google.com/document/d/e/2PACX-1vTr6HtjKNbF6u8pfRqhIDMVp-dV1GkQKpEMbL95vzDLhbuVaFMKyUeGi6S7FpLcCUW-YKi1enFJC6ZR/pub)

## Configuration File

In order to authenticate to ArchivesSpace and use the ArchivesSpace API, supply a "config.ini" file in the "avatar" directory that looks like this:

```
[ArchivesSpace]
BaseURL = 
User = 
Password = 
```

## A Note on Notes and Dates

## Access Restrictions

## Usage

## Output