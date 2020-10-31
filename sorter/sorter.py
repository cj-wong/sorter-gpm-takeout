import csv
from pathlib import Path
from typing import Dict, List, Union

import eyed3

from sorter import config


def sanitize(label: str) -> str:
    """Replace parts of a string with sanitized versions."""
    return label.replace('&amp;', '_').replace('&#39;', '\'')


class Sorter:
    """Sorter for GPM music.

    Attributes:
        metadata (Dict[str, Dict[str, str]]): metadata per track;
            contains a subset from that of track_data when loaded
        track_data (eyed3.id3.tag.Tag): track metadata; loaded from
            find_track()

    """

    def __init__(self) -> None:
        """Initialize metadata, so that music files will only be read once."""
        self.metadata = {}
        self.to_delete = []

    def sort(self) -> None:
        """Open all CSVs and get the corresponding track."""
        for file in config.TRACKS.glob('*.csv'):
            config.LOGGER.info(f'Now checking {file}')
            delete_ok = False
            # Title,Album,Artist,Duration (ms),Rating,Play Count,Removed
            for self.row in TrackCSV(file).read():
                track = self.find_track()
                if not track:
                    continue

                album_dir = self.make_dirs('Album', self.row['Album'])
                album_track = self.move_track(track, album_dir)

                self.extract_images()

                artist_dir = self.make_dirs('Artist', self.row['Artist'])
                self.link_track(album_track, artist_dir)

                # Check whether the track features multiple artists;
                # create the directories for each individual artist as well.
                if ('Orchestra' in self.row['Artist']
                        and ',' in self.row['Artist']):
                    pass
                else:
                    artists = self.row['Artist'].split(', ')
                    if len(artists) > 1:
                        for artist in artists:
                            artist_dir = self.make_dirs('Artist', artist)
                            self.link_track(album_track, artist_dir)
                delete_ok = True
            if delete_ok:
                self.to_delete.append(file)

    def make_dirs(self, category: str, element: str) -> Path:
        """Make a directory given category and element.

        Because `Path.mkdir` is supplied the arguments `parents` and
        `exist_ok`, the resulting behavior is similar to `mkdir -p`.

        Args:
            category (str): 'Album' or 'Artist'
            element (str): e.g. an artist or an album

        Returns:
            Path: the directory created

        """
        if element in config.CORR[f'{category}s']:
            element = config.CORR[f'{category}s']
        if element.startswith('http://'):
            element = element.replace('http://', '')
        out_dir = config.DEST / f'{category}s' / element
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def find_track(self) -> Union[Path, None]:
        """Find the track given artist.

        Tracks must also match album and title.

        Returns:
            Path: the file name and path for the matched track
            None: if no file matched - this must be addressed

        """
        artist = self.row['Artist']
        if '&amp;' in artist:
            artist = artist.replace('&amp;', '_')

        # Before checking more new files, check whether the track
        # has already been seen in self.metadata.
        for track, metadata in self.metadata.items():
            if (self.fuzzy_match(metadata['artist'], artist)
                    and self.fuzzy_match(metadata['album'], self.row['Album'])
                    and self.fuzzy_match(
                        metadata['title'], self.row['Title'])):
                try:
                    self.track_data = eyed3.load(track)
                    return track
                except OSError as e:
                    # Somehow, this happens quite a bit often with files
                    # that have duplicates (or near duplicates).
                    config.LOGGER.info('You may have had a duplicate.')
                    config.LOGGER.info(f'More info: {e}')
                    continue

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

            album = self.track_data.tag.album
            title = self.track_data.tag.title

            if (self.fuzzy_match(album, self.row['Album'])
                    and self.fuzzy_match(title, self.row['Title'])):
                return track

        # Nothing was found?
        # This can fail, if config.TRACKS.glob() couldn't find anything
        # with the artist name.
        try:
            del self.track_data
        except AttributeError:
            config.LOGGER.warning(
                'The following track did not have any hits on artist.'
                )

        config.LOGGER.warning(
            'Could not find a matching track file given the following:'
            )
        one_line = f'{self.row["Album"]}-{self.row["Title"]}-{artist}'
        config.LOGGER.warning(one_line)

    def extract_images(self) -> None:
        """Extract album images from the track."""
        album = self.track_data.tag.album
        for image in self.track_data.tag.images:
            img_file = config.DEST / 'Albums' / album / image.makeFileName()
            if img_file.exists():
                continue
            with img_file.open(mode='wb') as img:
                img.write(image.image_data)

    def move_track(self, track: Path, album: Path) -> Path:
        """Move a track from the Takeout folder into its album.

        Args:
            track (Path): the file and path of the track
            album (Path): the album directory

        Returns:
            Path: the renamed and moved track

        """
        dest = (
            album
            / config.FMT.format(**self.metadata[track]).replace('/', '_')
            )
        track.replace(dest)
        return dest

    def link_track(self, album_track: Path, artist: Path) -> None:
        """Link a track from its album to artists' directories.

        Args:
            track (Path): the file and path of the track
            artist (Path): the artist directory

        """
        dest = artist / album_track.name
        try:
            dest.symlink_to(album_track)
        except FileExistsError:
            config.LOGGER.warning(f'{dest} already exists as a symlink.')
            pass

    def delete_csv(self) -> None:
        """Delete files that have been successfully read."""
        for file in self.to_delete:
            file.unlink()

    def fuzzy_match(self, track_a_data: str, track_b_data: str) -> bool:
        """Check whether track_a_data and track_b_data fuzzy-match.

        So far, it seems ampersands break comparisons. As a result,
        ampersands will be ignored for comparison.

        Returns:
            bool: True if both track data match

        """
        if not track_a_data and not track_b_data:
            return True
        try:
            track_a_data = sanitize(track_a_data)
            track_b_data = sanitize(track_b_data)
        except AttributeError:
            # Because the case of being both has been handled earlier,
            # both data cannot match if one is empty.
            return False
        return track_a_data == track_b_data


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
