# Sorter for [Google] Play Music [Takeout]

## Overview

Google Play Music files can be exported via Google [Takeout]. However, the resulting file structure in the archives is flattened (see [below](#file-structure) for details) from the original (notably, no Albums listed) *and* many, if not most, of the files have truncated names.

In order to bring back structure, this project will iterate through the tracks and rebuild the albums list, possibly renaming the files as desired. To do so, the files in `Takeout/Google Play Music/Tracks` will be read for clues to piece the files together.

Furthermore, a [pattern](#format-structure) may be supplied in the configuration file to rename files in a way that better convey a track's metadata.

⚠ **This project is not ever intended to modify metadata. It is strictly to organize the tracks into separate directories based on album and artist(s) in the tracks' metadata.**

⚠ Please ensure all your music is intact *before* deleting the original Takeout archive files!

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

`*` Unfortunately, these fields can be missing/stripped from Takeout. Disc numbers will be updated to the default of 1 if missing, but track numbers can't be changed. In both cases, you will be alerted of the missing numbers and can take action later. Make sure to check the logs for `has missing` to pin-down the troublesome files.

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

⚠ **These corrections do not take in account any other context, only their associated field. This means that when a value matches, it will be unconditionally substituted with its replacement.**

For instance, if you put `"abc": "ABC"` under `"Artist"`, an artist (or group artist) whose name contains `abc` will now be changed to `ABC`, even if `abc` is in the middle of the name.

*If any of the fields are missing, they will be substituted with an empty dictionary within [config.py](sorter/config.py), but will not be used in corrections.*

## Disclaimer

This project is not affiliated with or endorsed by [Google]. See [LICENSE](LICENSE) for more detail.

[Google]: https://www.google.com
[Takeout]: https://takeout.google.com
