# avatar
AVATAR: Bentley A/V dAtabase To ARchivesspace (for `<dsc>` elements)

## Description
Creates or updates ArchivesSpace `<dsc>` archival and digital object elements using data output from the A/V Database

## Input

### A/V Database Export

This CLI, which supports the Bentley's A/V Database --> ArchivesSpace workflow, assumes a spreadsheet with the following columns as an input:

- resource id (not from A/V Database)*
- object id (not from A/V Database)*
- Type of obj id (not from A/V Database)* <-- _Parent_ | _Item_ | _Part_
- CollItem No*
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

### Kaltura Export

It also assumes an export from Kaltura with the following columns (which, when run against the script in `utils/create_access_profile_pickle.py`--with a CSV hard-coded into the script--is converted to a pickle file saved as `access_profiles.p` in the "avatar" directory) as an input:

- entry_id*
- accessControlId*

_Note: "876301" is reading room, "1694751" is public, and "2227181" is U-M campus._

## Update Collection-Level Information

With the `-c` (or `--coll_info`) argument, the following fields to the collection-level resource in ArchivesSpace:

- Extents: An extent statement is added with "_x_ digital audiovisual files".
- "Processing Information" note: Adds a `processinfo` note with `<extptr href="digitalproc" show="embed" actuate="onload">`. This in turn adds a note to DLXS, "In preparing digital material for long-term preservation and access, the Bentley Historical Library adheres to professional best practices and standards to ensure that content will retain its authenticity and integrity. For more information on procedures for the ingest and processing of digital materials, please see Bentley Historical Library Digital Processing Note. Access to digital material may be provided either as a direct link to an individual file or as a downloadable package of files bundled in a zip file."
- Revision Statements: Three revision statements are added with the date...
  - "Revised Extent Note, Processing Information Note and Existence and Location of Copies Note."
  - "Added links to digitized content."
  - "Added Conditions Governing notes for digitized content."
- "Existence and Locations of Copies" note: Adds a `altformavail` note with "Digitization: A number of recordings within this collection have been digitized. The resulting files are available for playback online or in the Bentley Library Reading Room according to rights. Original media are only available for staff use."

## Update Container List

With the `-d` (or `--dsc`) argument, the following occurs...

### Basic Logic

First, AVATAR characterizes each row in the spreadsheet to determine:

- whether the corresponding ArchivesSpace archival object is a _parent_, _item_, or _part_ of the row using the "Type of obj id" column;
- whether the row is an _item ONLY_ or and _item with parts_ using the "DigFile Calc" and "CollItem No" columns (i.e., if they match, it assumes it is an "item only" and if they don't it assumes it is an "item with parts"); and
- whether the row is _audio_ or _moving image_ using the "DigFile Calc" column (i.e., if there is an "SR" it is audio).

The basic logic for creating or updating archival objects and creating and linking digital objects in ArchivesSpace, is, then:

Expression | Statement
--- | ---
If the corresponding ArchivesSpace archival object is a _parent_ and the row is an _item only_... | ..._create_ a child archival object (including instance with top container), _create and link_ a digital object (preservation) to the child archival object, and, if it exists, _create and link_ digital object (access) to the child archival object.
Else if the corresponding ArchivesSpace archival object is an _item_ and the row is an _item only_... | ... _update_ the archival object, _create and link_ a digital object (preservation) to the archival object, and, if it exists, _create and link_ a digital object (access) to the archival object.
Else if the corresponding ArchivesSpace archival object is an _part_ and the row is an _item only_... | NOT APPLICABLE
Else if the corresponding ArchivesSpace archival object is a _parent_ and the row is an _item with parts_... | ..._create_ a child archival object for the _item_  (including instance with top container), _create and link_ a digital object (preservation) to the child archival object, _create_ a child archival object to the child archival object for the _part_, and, if it exists, _create and link_ a digital object (access) to the child archival object of the child archival object.
Else if the corresponding ArchivesSpace archival object is an _item_ and the row is an _item with parts_... | ..._update_ the archival object for the _item_, _create and link_ a digital object (preservation) to the archival object, _create_ a child archival for the _part_, and, if it exists, _create and link_ a digital object (access) to the child archival object for the _part_.
Else if the corresponding ArchivesSpace archival object is an _part_ and the row is an _item with parts_... | ..._update_ the parent archival object for the _item_, if it does not exist, _create and link_ a digital object (preservation) to the parent archival object, update the archival object for the _part_, and, if it exists, _create and link_ a digital object (access) to the archival object.

### Crosswalk: A/V Database --> ArchivesSpace

Key:

- "Quotation marks": Hard-coded
- _Italicized_: From the A/V Database export
- `Consolas`: From the ArchivesSpace API

#### Archival Objects

##### Items ONLY

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
  - Physical Details = ", ".join(_AVType::Avtype_, _ItemColor_ (optional), _ItemPolarity_ (optional), _ItemSound_ (optional), _AUDIO_ITEMCHAR::Fidleity_ (optional), _AUDIO_ITEMCHAR::TapeSpeed_ (optional))
  - Dimensions = ", ".join(_AUDIO_ITEMCHAR::ReelSize_ (optional), _ItemLength_ (optional), _AUDIO_ITEMCHAR::ItemSourceLength_ (optional))
- Notes
  - Note (Optional)
    - Type = "Abstract"
    - Text = _NoteContent_
  - Note (Optional)
    - Type = "General"
    - Content = _ItemTime_ (optional)
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

##### Items with Parts

###### Item

- Title = _ItemTitle_
- Level of Description = "Other Level"
- Other Level = "item-main"
- Extents
  - Portion = "Whole"
  - Number = "1"
  - Type = _AVType::ExtentType_
  - Physical Details = ", ".join(_AVType::Avtype_, _ItemColor_ (optional), _ItemPolarity_ (optional), _ItemSound_ (optional), _AUDIO_ITEMCHAR::Fidleity_ (optional), _AUDIO_ITEMCHAR::TapeSpeed_ (optional))
  - Dimensions = ", ".join(_AUDIO_ITEMCHAR::ReelSize_ (optional), _ItemLength_ (optional), _AUDIO_ITEMCHAR::ItemSourceLength_ (optional))
- Instances
  - Top Container
    - Indicator = `indicator`
    - Container Type = `type`    

###### Parts

- Title = _ItemPartTitle_
- Component Unique Identifier = _DigFile Calc_
- Level of Description = "Other Level"
- Other Level = "item-part"
- Dates (see "A Note on Dates and Notes")
  - Label = "Creation"
  - Expression = _ItemDate_
  - Type = "Inclusive Dates"
- parent = Archival Object (Item) `uri`
- Notes
  - Note (Optional) (see "A Note on Dates and Notes")
    - Type = "Abstract"
    - Text = _NoteContent_
  - Note (Optional)
    - Type = "General"
    - Content = _ItemTime_ (optional)
  - Note (Optional)
    - Type = "Conditions Governing Access"
    - Text = "Access to this material is restricted to the reading room of the Bentley Historical Library." OR "Access to digitized content is enabled for users who are able to authenticate via the University of Michigan weblogin."
  - Note (Optional)
    - Type = "General"
    - Publish = False
    - Text = "Internal Technical Note: " + _NoteContent_

###### A Note on Dates and Notes

If multiple parts of the same item have the same date or same Conditions Governing Access note, the date and Conditions Governing Access note will be applied to the _item_. Otherwise, they will be applied to the _parts_. #comingsoon

#### Digital Objects

##### Preservation

- Title = Archival Object (Item) `display_string` + " (Preservation)"
- Identifier = DigFile Calc (Item) (i.e., "07143-70" in "07143-70-1" or "07143-SR-63" in "07143-SR-63-1")
- Publish? = False
- File Versions
  - File URI = "R:/AV Collections/" + ("Audio" or "Moving Image") + "/" + Collection ID (i.e., "9841" in "9841 Bimu 2" or "umich-bhl-9841") + "/" + DigFile Calc (Item) (i.e., "07143-70" in "07143-70-1" or "07143-SR-63" in "07143-SR-63-1")

##### Access

- Title = Archival Object (Item) `display_string` + " " + Archival Object (Part) `display_string` + " (Access)"
Identifier = _MiVideoID_
- File Versions
  - File URI = "https://bentley.mivideo.it.umich.edu/media/t/" + _MiVideoID_
  - XLink Actuate Attribute = "onRequest"
  - XLink Show Attribute = "new"

### Configuration File

In order to authenticate to ArchivesSpace and use the ArchivesSpace API, supply a "config.ini" file in the "avatar" directory that looks like this:

```
[ArchivesSpace]
BaseURL = ''
User = ''
Password = ''
RepositoryID = ''
```

### Access Restrictions

#comingsoon

## Usage

```
usage: avatar.py [-h] [-c COLLECTION_LEVEL_INFO] [-d DSC]
                 [-o /path/to/output/directory]
                 /path/to/project/csv.csv

Creates or updates ArchivesSpace `<dsc>` archival and digital object elements
using data output from the A/V Database

positional arguments:
  /path/to/project/csv.csv
                        Path to a project CSV

optional arguments:
  -h, --help            show this help message and exit
  -c COLLECTION_LEVEL_INFO, --collection-level_info COLLECTION_LEVEL_INFO
                        Updates collection-level-information
  -d DSC, --dsc DSC     Updates container list
  -o /path/to/output/directory, --output /path/to/output/directory
                        Path to output directory for result
```

## Output

AVATAR outputs a CSV file with the DigFile Calc (for the Item or Part, depending on whether it's an "item ONLY" or "item with parts," respectively) and the corresponding `archival_object_id`. This can be used to update the A/V Database. The optional `--output` argument can be used to specify a destination directory.

#comingsoon
