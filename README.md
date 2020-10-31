# Sorter for [Google] Play Music [Takeout]

## Overview

Google Play Music files can be exported via Google [Takeout]. However, the resulting file structure in the archives is flattened (see [below](#file-structure) for details) from the original (notably, no Albums listed).

In order to bring back structure, this project will read through the files and rebuild the albums list and possibly rename the files as desired. To do so, the MP3s in `Takeout/Google Play Music/Tracks` will be read for clues to piece the files together.

**This project is not ever intended to modify metadata. It is strictly to organize the tracks into separate directories based on album and artist(s).**

## File structure

When you extract the files from the archives, you will end up with a file structure like this:

```
Takeout/
├── archive_browser.html
└── Google Play Music
    ├── Playlists
    │   ├── Playlist A
    │   │   ├── Metadata.csv
    │   │   └── Tracks
    │   │       ├── Track1.csv
    │   │       └── Track2.csv
    │   ├── Shuffle
    │   │   ├── Metadata.csv
    │   │   └── Tracks
    │   │       ├── Track1.csv
    │   │       └── Track2.csv
    │   └── Thumbs Up
    │       ├── Track1.csv
    │       └── Track2.csv
    ├── Radio Stations
    │   ├── My Stations
    │   │   └── Station1.csv
    │   └── Recent Stations
    │       ├── Station1.csv
    │       └── Station2.csv
    └── Tracks
        ├── Track1.csv
        ├── Track2.csv
        ├── Track1.mp3
        └── Track2.mp3
```

## Format Structure

In the [configuration](config.json.example) file, `"format"` dictates how a file will be renamed. This value is a Python pre-formatted string, to be used with `str.format()`.

The following fields are available:

- `artist`: the primary artist(s) of the track
- `album`: the album in which this track belongs
- `title`: title of the track
- `disc_num`: disc number; goes from 1 `*` to `disc_max`
- `disc_max`: number of discs that belong to the album
- `track_num`: track number; goes from 1 `*` to `track_max`
- `track_max`: number of tracks on an album's disc containing the track

To use these fields, simply insert the field name anywhere you prefer and surround the field with curly braces, like so: `{artist}`.

`*` Unfortunately, these fields can be missing/stripped from Takeout. I'm unsure what the mechanic is for the deletion of this data, but both disc numbers and both track numbers can be 0.

## Usage

1. Configure [config.json](config.json.example) by copying the example and renaming it. You may use tildes (`~`) to represent your home directory. You can also change the file name format.
2. Optionally, configure `corrections.json`. This file has the structure of a dictionary with up to 3 keys (`"Artist"`, `"Album"`, `"Title"`), with each key having dictionaries that transform values from the key to the value. For example, if a track spells an artist in all caps and normally the artist isn't spelled all caps, you can put the all caps name under `"Artist"` and assign it the expected value.
3. Run `python main.py`.

## Requirements

This code is designed around the following:

- Python 3.7+
    - `eyed3` for parsing the MP3 metadata
    - other [requirements](requirements.txt)

## Setup

[config.json](config.json.example)

- `"format"`: a Python pre-formatted string; see [Format Structure](#format-structure)
- `"takeout_dir"`: a string that represents the path to `Takeout` (must end in `Takeout`)
- `"dest_dir"`: a string that represents the destination directory, where subdirectories `Artists` and `Albums` will reside

`corrections.json` (optional)

- `"Artist"`
- `"Album"`
- `"Title"`

⚠ **These corrections do not take in account any other context, only their associated field.**

If any of the fields are missing, they will be substituted with an empty dictionary within [config.py](sorter/config.py).

## Disclaimer

This project is not affiliated with or endorsed by [Google]. See [LICENSE](LICENSE) for more detail.

[Google]: https://www.google.com
[Takeout]: https://takeout.google.com
