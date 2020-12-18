import re
from pathlib import Path

import eyed3

from sorter import config


SUFFIX = re.compile(r'[,_] ([js]r)', re.IGNORECASE)


def sanitize(label: str, category: str) -> str:
    """Replace parts of a string with sanitized versions.

    The only character that cannot match its intended character
    is the slash '/', since slashes are part of paths.

    """
    if label in config.CORR[category]:
        label = config.CORR[category]

    try:
        return (label.replace('&amp;', '&').replace('&#39;', '\'')
                .replace('&quot;', '"').replace('/', '_').replace(';', ','))
    except AttributeError:
        # I think only artists may be empty
        return None


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
        pass

    def sort(self) -> None:
        """Sort all MP3s given their ID3 metadata."""
        for track in config.TRACKS.glob('*.mp3'):
            config.LOGGER.info(f'Now checking {track}')
            has_album = True
            self.track_data = eyed3.load(track)
            track_min, track_max = self.track_data.tag.track_num
            if track_min == 0 or track_max == 0:
                config.LOGGER.warning(f'{track} has missing track number(s)!')
            disc_min, disc_max = self.track_data.tag.disc_num
            if disc_min == 0:
                config.LOGGER.warning(f'{track} has missing disc number!')
                disc_min = 1
            if disc_max == 0:
                config.LOGGER.warning(
                    f'{track} has missing total disc number per album!')
                disc_max = 1
            self.metadata = {
                'artist': sanitize(self.track_data.tag.artist, 'Artist'),
                'album': sanitize(self.track_data.tag.album, 'Album'),
                'title': sanitize(self.track_data.tag.title, 'Title'),
                'track_num': track_min,
                'track_max': track_max,
                'disc_num': disc_min,
                'disc_max': disc_max,
                }

            try:
                album_dir = self.make_dirs('Album', self.metadata['album'])
            except KeyError:
                # This isn't an album track, but when no album is present,
                # the group artists are used instead while retaining
                # the original variable name.
                album_dir = self.make_dirs('Artist', self.metadata['artist'])
                has_album = False

            album_track = self.move_track(track, album_dir)
            self.extract_images(album_dir)

            if not self.metadata['artist']:
                continue

            if has_album:
                artist_dir = self.make_dirs('Artist', self.metadata['artist'])
                self.link_track(album_track, artist_dir)

            self.metadata['artist'] = self.substitute_suffixes(
                self.metadata['artist'], '_')

            # Orchestra music can't be put into separate artists' directories
            # due to metadata mangling. e.g. Person A, composer, Person B
            # Unfortunately, due to string splitting to commas, "composer"
            # would be interpreted as a valid artist.
            if self.handle_orchestra():
                pass
            else:
                artists = self.metadata['artist'].split(', ')
                if len(artists) > 1:
                    for artist in artists:
                        # Replace potential swap from substitute_suffixes().
                        artist = self.substitute_suffixes(artist, ',')
                        artist_dir = self.make_dirs('Artist', artist)
                        self.link_track(album_track, artist_dir)

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
        out_dir = config.DEST / f'{category}s' / element
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def extract_images(self, album: Path) -> None:
        """Extract album images from the track.

        Args:
            album (Path): the file and path of the album

        """
        for image in self.track_data.tag.images:
            img_file = album / image.makeFileName()
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
            / config.FMT.format(**self.metadata)
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

    def handle_orchestra(self) -> None:
        """Handle orchestra, because why is conductor comma separated.

        Not sure why this is such a trouble, but lots of the orchestral
        music in my library have this problem.

        """
        return (',' in self.metadata['artist']
                and ('Orchestra' in self.metadata['artist']
                     or 'cello' in self.metadata['artist']
                     or 'conductor' in self.metadata['artist']
                     or 'Conductor' in self.metadata['artist']
                     or 'composer' in self.metadata['artist']
                     or 'Composter' in self.metadata['artist'] # FFS
                     or 'harpsichord' in self.metadata['artist']
                     or 'flute' in self.metadata['artist']
                     or 'piano' in self.metadata['artist']
                     or 'Soloist' in self.metadata['artist']
                     or 'violin' in self.metadata['artist'])
                )

    def substitute_suffixes(self, artist: str, separator: str) -> str:
        """Substitute suffixes, e.g. Someone, Jr. turns into Someone_ Jr.

        The artist(s) name can also be converted back as necessary.

        Args:
            artist (str): artist metadata
            separator (str): either comma or underscore

        Returns:
            str: the metadata with suffixes transformed

        """
        return SUFFIX.sub(rf'{separator} \1', artist)
