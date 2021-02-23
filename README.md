# avatar
AVATAR: Bentley A/V dAtabase To ARchivesspace (for `<dsc>` elements)

## Description
Add ArchivesSpace <dsc> elements from data output from the A/V Database.

## Input

This CLI, which supports the Bentley's A/V Database --> ArchivesSpace workflow, assumes a spreadsheet with the following columns as an input:

- resource id (not from A/V Database)*
- object id (not from A/V Database)*
- Type of obj id (not from A/V Database)* <-- _Parent_ | _Item_ | _Part_
- DigFile Calc*
- AVType::ExtentType*
- AVType::Avtype*
- ItemTitle*
- ItemPartTitle
- ItemDate*
- MiVideoID
- NoteContent
- NoteTechnical
- AUDIO_ITEMCHAR::Fidleity
- AUDIO_ITEMCHAR::ReelSize
- AUDIO_ITEMCHAR::TapeSpeed
- AUDIO_ITEMCHAR::ItemSourceLength
- ItemPolarity
- ItemColor
- ItemSound
- ItemLength
- ItemTime

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
If the corresponding ArchivesSpace archival object is a _parent_ and the row is an _item only_... | ..._create_ a child archival object (including instance with top container), _create and link_ a digital object (preservation) to the child archival object, and, if it exists, _create and link_ digital object (access) to the child archival object.
Else if the corresponding ArchivesSpace archival object is an _item_ and the row is an _item only_... | ... _update_ the archival object, _create and link_ a digital object (preservation) to the archival object, and, if it exists, _create and link_ a digital object (access) to the archival object.
Else if the corresponding ArchivesSpace archival object is an _part_ and the row is an _item only_... | NOT APPLICABLE
Else if the corresponding ArchivesSpace archival object is a _parent_ and the row is an _item with parts_... | ..._create_ a child archival object for the _item_  (including instance with top container), _create and link_ a digital object (preservation) to the child archival object, _create_ a child archival object to the child archival object for the _part_, and, if it exists, _create and link_ a digital object (access) to the child archival object of the child archival object.
Else if the corresponding ArchivesSpace archival object is an _item_ and the row is an _item with parts_... | ..._update_ the archival object for the _item_, _create and link_ a digital object (preservation) to the archival object, _create_ a child archival for the _part_, and, if it exists, _create and link_ a digital object (access) to the child archival object for the _part_.
Else if the corresponding ArchivesSpace archival object is an _part_ and the row is an _item with parts_... | ..._update_ the parent archival object for the _item_, _create and link_ a digital object (preservation) to the parent archival object, update the archival object for the _part_, and, if it exists, _create and link_ a digital object (access) to the archival object.

## Crosswalk: A/V Database --> ArchivesSpace

Key:

- "Quotation marks": Hard-coded
- _Italicized_: From the A/V Database export
- `Consolas`: From the ArchivesSpace API

### Archival Objects

#### Items ONLY

- Title = _ItemTitle_ OR (_ItemTitle_ + " " + _ItemPartTitle_ (optional))
- Component Unique Identifier = _DigFile Calc_
- Level of Description = "File"
- Dates
  - Label = "Creation"
  - Expression = _ItemDate_
  - Type = "Inclusive Dates"
- Extents
  - Portion = "Whole"
  - Number = "1"
  - Type = _AVType::ExtentType_
  - Physical Details = + _AVTYPE::AvType_
  - Dimensions = _AUDIO_ITEMCHAR::ReelSize_ (optional)
- Notes
  - Note
    - Type = "Abstract"
    - Text = _NoteContent_
    - Type = "Physical Facet"
    - Content = (", ".join(_AUDIO_ITEMCHAR::Fidleity_ (optional), _AUDIO_ITEMCHAR::TapeSpeed_ (optional), _AUDIO_ITEMCHAR::ItemSourceLength_ (optional), _ItemPolarity_ (optional), _ItemColor_ (optional), _ItemSound_ (optional), _ItemLength_ (optional), _ItemTime_ (optional)))
  - Note (Optional)
    - Type = "Conditions Governing Access"
    - Text = "Access to this material is restricted to the reading room of the Bentley Historical Library." OR "Access to digitized content is enabled for users who are able to authenticate via the University of Michigan weblogin."
  - Note (Optional)
    - Type = "General"
    - Publish = False
    - Text = "Internal Technical Note: " + _NoteContent_
- Instances
  - Top Container
    - Indicator = `indicator`
    - Container Type = `type`   

#### Items with Parts

##### Item

- Title = _ItemTitle_
- Level of Description = "Other Level"
- Other Level = "item-main"
- Extents
  - Portion = "Whole"
  - Number = "1"
  - Type = _AVType::ExtentType_
  - Physical Details = _AVType::Avtype_
  - Dimensions = _AUDIO_ITEMCHAR::ReelSize_ (optional)
- Instances
  - Top Container
    - Indicator = `indicator`
    - Container Type = `type`    

##### Parts

- Title = _ItemPartTitle_
- Component Unique Identifier = _DigFile Calc_
- Level of Description = "Other Level"
- Other Level = "item-part"
- Dates (see "A Note on Dates and Notes")
  - Label = "Creation"
  - Expression = _ItemDate_
  - Type = "Inclusive Dates"
parent = Archival Object (Item) `uri`
- Notes
  - Note (see "A Note on Dates and Notes")
    - Type = "Abstract"
    - Text = _NoteContent_
  - Note
    - Type = "Physical Facet"
    - Content = (", ".join(_AUDIO_ITEMCHAR::Fidleity_ (optional), _AUDIO_ITEMCHAR::TapeSpeed_ (optional), _AUDIO_ITEMCHAR::ItemSourceLength_ (optional), _ItemPolarity_ (optional), _ItemColor_ (optional), _ItemSound_ (optional), _ItemLength_ (optional), _ItemTime_ (optional)))
  - Note (Optional)
    - Type = "Conditions Governing Access"
    - Text = "Access to this material is restricted to the reading room of the Bentley Historical Library." OR "Access to digitized content is enabled for users who are able to authenticate via the University of Michigan weblogin."
  - Note (Optional)
    - Type = "General"
    - Publish = False
    - Text = "Internal Technical Note: " + _NoteContent_

##### A Note on Dates and Notes

If multiple parts of the same item have the same date or same Conditions Governing Access note, the date and Conditions Governing Access note will be applied to the _item_. Otherwise, they will be applied to the _parts_.

### Digital Objects

#### Preservation

- Title = Archival Object (Item) `display_string` + " (Preservation)"
- Identifier = DigFile Calc (Item) (i.e., "07143-70" in "07143-70-1" or "07143-SR-63" in "07143-SR-63-1")
- Publish? = False
- File Versions
  - File URI = "R:/AV Collections/" + ("Audio" or "Moving Image") + "/" + Collection ID (i.e., "9841" in "9841 Bimu 2" or "umich-bhl-9841") + "/" + DigFile Calc (Item) (i.e., "07143-70" in "07143-70-1" or "07143-SR-63" in "07143-SR-63-1")

#### Access

- Title = Archival Object (Item) `display_string` + " " + Archival Object (Part) `display_string` + " (Access)"
Identifier = _MiVideoID_
- File Versions
  - File URI = "https://bentley.mivideo.it.umich.edu/media/t/" + _MiVideoID_
  - XLink Actuate Attribute = "onRequest"
  - XLink Show Attribute = "new"

## Configuration File

In order to authenticate to ArchivesSpace and use the ArchivesSpace API, supply a "config.ini" file in the "avatar" directory that looks like this:

```
[ArchivesSpace]
BaseURL = ''
User = ''
Password = ''
RepositoryID = ''
```

## Access Restrictions

#comingsoon

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

#comingsoon
