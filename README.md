# Sorter for [Google] Play Music Takeout

## Overview

Google Play Music files can be exported via Google [Takeout]. However, the resulting file structure in the archives is flattened (see [below](#file-structure) for details) from the original (notably, no Albums listed).

In order to bring back structure, this project will read through the files and rebuild the albums list and possibly rename the files as desired. To do so, the CSVs in `Takeout/Google Play Music/Tracks` will be read for clues to piece the files together.

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

Each subdirectory (`Playlists`, etc.) has its own kind of CSV structure. This project will concentrate on the subdirectory `Tracks` and the CSVs there.

A track CSV may look like:

```
Title,Album,Artist,Duration (ms),Rating,Play Count,Removed
"Track Title","Album Name","Artist Name","0","0","0",""
```

**It's important to note that although in the tree structure I list `Track1.csv` and a corresponding `Track1.mp3`, they will most likely never match.** The track file name generally is `Artist - Album - Title.mp3`, but sometimes the track title matches the file name. Other times, it's a mix of artist name, track name, and/or album name.

Therefore, the CSV will get a general idea of the matching file, create the album directory if needed, read all files that may match for their ID3 tags, and move the right file to the album directory (and possibly rename, if desired).

## Format Structure

In the [configuration](config.json.example) file, `"format"` dictates how a file will be renamed. This value is a Python pre-formatted string, to be used with `str.format()`.

The following fields are available:

- `artist`: the primary artist(s) of the track
- `album`: the album in which this track belongs
- `title`: title of the track
- `disc_num`: disc number; goes from 1 to `disc_max`
- `disc_max`: number of discs that belong to the album
- `track_num`: track number; goes from 1 to `track_max`
- `track_max`: number of tracks on an album's disc containing the track

To use these fields, simply insert the field name anywhere you prefer and surround the field with curly braces, like so: `{artist}`.

## Usage

TODO

## Requirements

This code is designed around the following:

- Python 3.7+
    - TODO
    - other [requirements](requirements.txt)

## Setup

1. TODO

## Live Version

These files are generated/updated every X.

- n/a

## Disclaimer

This project is not affiliated with or endorsed by [Google]. See [LICENSE](LICENSE) for more detail.

[Google]: https://www.google.com
[Takeout]: https://takeout.google.com
