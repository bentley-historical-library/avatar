# avatar
AVATAR: Bentley A/V dAtabase To ARchivesspace

![AVATAR logo](Avatar_V3.png)

_Image Credit: Melissa Hernández-Durán_

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

You will need to do a little cleanup on the source .XLSX file. Convert it to a UTF-8 encoded CSV, and clean up any character encoding issues, e.g., fractions in AUDIO_ITEMCHAR::TapeSpeed and formatting in ItemTime.

### Configurations for ArchivesSpace Instances

It also assumes a configuration file detailing both DEV and PROD ArchivesSpace instances.

### Kaltura Export and Conditions Governing Access Notes

Finally, it assumes an export from Kaltura with the following columns (which, when run against the script in `utils/create_access_profile_pickle.py`--with a CSV hard-coded into the script--is converted to a pickle file saved as `access_profiles.p` in the "avatar" directory) as an input:

- entry_id*
- accessControlId*

_Note: "876301" is reading room, "1694751" is public, and "2227181" is U-M campus._

AVATAR reads the pickle file and determines the appropriate Conditions Governing Access note.

## Update Collection-Level Information

With the `-c` (or `--coll_info`) argument, the following fields to the collection-level resource in ArchivesSpace:

- Extents: An extent statement is added with "_x_ digital audio files" or "_x_ digital video files," accordingly. It also ensures that all extent portions have the value of "Part."
- "Processing Information" note: Adds a `processinfo` note with `<extptr href="digitalproc" show="embed" actuate="onload">`. This in turn adds a note to DLXS, "In preparing digital material for long-term preservation and access, the Bentley Historical Library adheres to professional best practices and standards to ensure that content will retain its authenticity and integrity. For more information on procedures for the ingest and processing of digital materials, please see Bentley Historical Library Digital Processing Note. Access to digital material may be provided either as a direct link to an individual file or as a downloadable package of files bundled in a zip file."
- Revision Statements: Four revision statements are added with the date...
  - "Revised Extent Note, Processing Information Note and Existence and Location of Copies Note."
  - "Added links to digitized content."
  - "Added Conditions Governing notes for digitized content."
  - "Added audio recording genre." OR "Added video recording genre."
- "Existence and Locations of Copies" note: Adds a `altformavail` note with "Digitization: A number of recordings within this collection have been digitized. The resulting files are available for playback online or in the Bentley Library Reading Room according to rights. Original media are only available for staff use."
- "Conditions Governing Access" note: Adds a `accessrestrict` note with "Select recordings within this collection have been digitized. Original sound recordings are only available for staff use."
- Genre/Form: Adds the appropriate ArchivesSpace subjects for "sound recording" and "video recording."

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
If the corresponding ArchivesSpace archival object is a _parent_ and the row is an _item only_... | ..._create_ a child archival object (including instance with top container), if not a duplicate, _create and link_ a digital object (preservation) to the child archival object, and, if it exists, _create and link_ digital object (access) to the child archival object.
Else if the corresponding ArchivesSpace archival object is an _item_ and the row is an _item only_... | ... _update_ the archival object, if not a duplicate, _create and link_ a digital object (preservation) to the archival object, and, if it exists, _create and link_ a digital object (access) to the archival object.
Else if the corresponding ArchivesSpace archival object is an _part_ and the row is an _item only_... | NOT APPLICABLE
Else if the corresponding ArchivesSpace archival object is a _parent_ and the row is an _item with parts_... | ..._create_ a child archival object for the _item_  (including instance with top container), _create and link_ a digital object (preservation) to the child archival object, _create_ a child archival object to the child archival object for the _part_, and, if it exists, _create and link_ a digital object (access) to the child archival object of the child archival object.
Else if the corresponding ArchivesSpace archival object is an _item_ and the row is an _item with parts_... | ..._update_ the archival object for the _item_, _create and link_ a digital object (preservation) to the archival object, _create_ a child archival for the _part_, and, if it exists, _create and link_ a digital object (access) to the child archival object for the _part_.
Else if the corresponding ArchivesSpace archival object is an _part_ and the row is an _item with parts_... | ..._update_ the parent archival object for the _item_, if it does not exist, _create and link_ a digital object (preservation) to the parent archival object, update the archival object for the _part_, and, if it exists, _create and link_ a digital object (access) to the archival object.

_Note: AVATAR identifies recordings that are duplicates that were not digitized (but still need to be tracked for collections management purposes) if the row is an item only but there is no MiVideoID._

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
- Component Unique Identifier = _CollItem No_
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
- Dates
  - Label = "Creation"
  - Expression = _ItemDate_
  - Type = "Inclusive Dates"
- parent = Archival Object (Item) `uri`
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

#### Digital Objects

##### Preservation

- Title = Archival Object (Item) `display_string` + " (Preservation)"
- Identifier = DigFile Calc (Item) (i.e., "07143-70" in "07143-70-1" or "07143-SR-63" in "07143-SR-63-1")
- Publish? = False
- File Versions
  - File URI = "\\bhl-digitalarchive.m.storage.umich.edu\bhl-digitalarchive/AV Collections/" + ("Audio" or "Moving Image") + "/" + Collection ID (i.e., "9841" in "9841 Bimu 2" or "umich-bhl-9841") + "/" + DigFile Calc (Item) (i.e., "07143-70" in "07143-70-1" or "07143-SR-63" in "07143-SR-63-1")

##### Access

- Title = Archival Object (Item) `display_string` + " " + Archival Object (Part) `display_string` + " (Access)"
Identifier = _MiVideoID_
- File Versions
  - File URI = "https://bentley.mivideo.it.umich.edu/media/t/" + _MiVideoID_
  - XLink Actuate Attribute = "onRequest"
  - XLink Show Attribute = "new"

### Configuration File

In order to configure the baseline preservation path, authenticate to ArchivesSpace, and use the ArchivesSpace API, supply a "config.ini" file in the "avatar" directory that looks like this:

```
[PRESERVATION]
BasePreservationPath = ``

# These are configurations for ArchivesSpace instances
[DEV]
BaseURL = ''
User = ''
Password = ''
RepositoryID = '' # Note: AVATAR assumes a default ArchivesSpace repository ID of 2.

[PROD]
BaseURL = ''
User = ''
Password = ''
RepositoryID = '' # Note: AVATAR assumes a default ArchivesSpace repository ID of 2.

[SANDBOX]
BaseURL = ''
User = ''
Password = ''
RepositoryID = '' # Note: AVATAR assumes a default ArchivesSpace repository ID of 2.
```

## Usage

```
usage: avatar.py [-h] [-c] [-d] [-r] [-o /path/to/output/directory] /path/to/project/csv.csv {dev,prod,sandbox}

Creates or updates ArchivesSpace `<dsc>` archival and digital object elements using data output from the A/V Database

positional arguments:
  /path/to/project/csv.csv
                        Path to a project CSV
  {dev,prod,sandbox}    Choose configuration for DEV, PROD, or SANDBOX ArchivesSpace instance

optional arguments:
  -h, --help            show this help message and exit
  -c, --coll_info       Updates collection-level-information
  -d, --dsc             Updates container list
  -r, --revert_back     Undoes collection- and container-level updates
  -o /path/to/output/directory, --output /path/to/output/directory
                        Path to output directory for results
```

## Output

AVATAR outputs a CSV file with the DigFile Calc (for the Item or Part, depending on whether it's an "item ONLY" or "item with parts," respectively) and the corresponding `archival_object_id`. This can be used to update the A/V Database. The optional `--output` argument can be used to specify a destination directory.

## Cache

AVATAR creates a cache of resources it updates as well as archival objects and digital objects it creates (ID only) or updates (JSON) for individual media files (`digfile_calcs`). To iniate the cache, use `utils/create_digfile_calcs_pickle.py` and ensure that there is a "cache" directory with a "resources" and "digfile_calcs" subdirectories in the home folder. For resources, they are simply stored in a cached JSON representation of the resource in a file named `[resource_id].json`. Media files, however, are stored in a pickle structured like:

```
[{
	'85242-1': [{
		'type': 'archival_object',
		'id': '371206',
		'status': 'updated'
	}, {
		'type': 'digital_object',
		'id': '43062',
		'status': 'created'
	}, {
		'type': 'digital_object',
		'id': '43063',
		'status': 'created'
	}]
}]
```

Any updated archival objects are stored in a file named "[archival_object_id].json."

## Revert Back (In Development)

AVATAR can use the cache it creates to "revert back" to a previous state, i.e., to undo collection- and container-level updates. This should only be use in a non-PROD environment.
