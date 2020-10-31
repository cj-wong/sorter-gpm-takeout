import csv
from pathlib import Path
from typing import Dict, List, Union

import eyed3

from sorter import config


class Sorter:
    """Sorter for GPM music.

    Attributes:
        CATEGORIES (Tuple[str]): categories to sort music
        metadata (Dict[str, Dict[str, str]]): metadata per track

    """

    CATEGORIES = ('Album', 'Artist')

    def __init__(self) -> None:
        """Initialize metadata, so that music files will only be read once."""
        self.metadata = {}

    def sort(self) -> None:
        """Open all CSVs and get the corresponding track."""
        for file in config.TRACKS.glob('*.csv'):
            # Title,Album,Artist,Duration (ms),Rating,Play Count,Removed
            for self.row in TrackCSV(file).read():
                self.find_track()
                for category in self.CATEGORIES:
                    self.make_dirs(category)

                # Check whether the track features multiple artists;
                # create the directories for each individual artist as well.
                artists = self.row['Artist'].split(', ')
                if len(artists) > 1:
                    for artist in artists:
                        self.make_dirs('Artist', artist)

    def make_dirs(self, category: str, element: str) -> None:
        """Make a directory given category and element.

        Because `Path.mkdir` is supplied the arguments `parents` and
        `exist_ok`, the resulting behavior is similar to `mkdir -p`.

        Args:
            category (str): 'Album' or 'Artist'
            element (str): e.g. an artist or an album

        """
        out_dir = config.DEST / f'{category}s' / element
        out_dir.mkdir(parents=True, exist_ok=True)

    def find_track(self) -> Union[Path, None]:
        """Find the track given artist.

        Tracks must also match album and title.

        Returns:
            Path: the file name and path for the matched track
            None: if no file matched - this must be addressed

        """
        artist = self.row['Artist']

        for track, metadata in self.metadata.items():
            if (metadata['artist'] == artist
                    and metadata['album'] == self.row['Album']
                    and metadata['title'] == self.row['Title']):
                self.track_data = eyed3.load(track)
                return track

        # There is an exception to this pattern, and I'm unsure how
        # it'll be matched with its corresponding CSV.
        # Exception: _Yoshi_s Island_) - Super Smash Bros. for (011).mp3
        for track in config.TRACKS.glob(f'{artist} - *.mp3'):
            # Don't read metadata from already read tracks
            if track in self.metadata:
                continue
            self.track_data = eyed3.load(track)
            track_min, track_max = self.track_data.tag.track_num
            disc_min, disc_max = self.track_data.tag.disc_num
            self.metadata[track] = {
                'artist': self.track_data.tag.artist,
                'album': self.track_data.tag.album,
                'title': self.track_data.tag.title,
                'track_num': track_min,
                'track_max': track_max,
                'disc_num': disc_min,
                'disc_max': disc_max,
                }

            if (self.track_data.tag.album == self.row['Album']
                    and self.track_data.tag.title == self.row['Title']):
                return track

    def extract_images(self) -> None:
        """Extract album images from the track."""
        album = self.track_data.tag.album
        for image in self.track_data.tag.images:
            img_file = config.DEST / 'Albums' / album / image.makeFileName()
            with img_file.open(mode='wb') as img:
                img.write(image.image_data)


class TrackCSV:
    """Represents a track CSV, representing a track by its metadata."""

    def __init__(self, file: Path) -> None:
        """Load a file into the csv reader, returning its row(s)."""
        self.file = file

    def read(self) -> List[Dict[str, str]]:
        """Read the CSV and dump the rows to a list, to return.

        Returns:
            List[Dict[str, str]]: a list (probably of length 1) with
                track metadata

        """
        rows = []
        with self.file.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        return rows
