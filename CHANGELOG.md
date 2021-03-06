# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.3.0] - 2021-03-11
### Changed
- In [sorter.py]:
    - In `Sorter.sort()`:
        - `album_dir` was renamed to a more accurate `parent_dir`. (The class method `Sorter.move_track()` similarly had its argument `album` renamed to `parent`.)
        - The initial assignment of `self.metadata` is now enclosed in `try: except TypeError:`. I discovered that if all metadata is stripped from a track, its tag becomes `None` rather than an empty `dict` and thus not subscriptable. The file is moved to `dest/no_tags`. See Issue #3.
        - Tracks that lack both artist and album tags are also moved to `dest/no_tags`. See Issue #3.

### Fixed
- Issue #3: Tracks that are missing either all metadata or just both artist and album tags will be moved into a separate 
- Issue #4: Total track count is kept during sorting and checked at the end to ensure it matches the pre-sort count.

## [0.2.3] - 2021-01-03
### Changed
- In [sorter.py]:
    - The `label` argument for `sanitize()` did not accurately appear to be optional (i.e. can be `None`); as a result and linted with `mypy`, `label` is now of type `Optional[str]`.
        - **Because of this distinction of `label` being possibly empty, the argument order for `sanitize()` is now `category: str, label: Optional[str]`.**
    - The `try: except AttributeError:` block might not be necessary now, since `mypy` encourages a literal `None` check at the beginning.
    - A new method-local variable `artist` is used in place of `self.metadata['artist']` in `Sorter.sort()`, with another `None` check to ensure `mypy` doesn't complain about mismatching types.
        - This allowed me to keep `Sorter.is_artist_orchestra()` and `Sorter.substitute_suffixes` relatively unchanged.

## [0.2.2] - 2021-01-02
### Changed
- The project has now been linted additionally by `mypy` on top of `Flake8`.

### Fixed
- In [sorter.py]:
    - In `sanitize()`, `label` was being incorrectly assigned `config.CORR[category]`, when in fact `config.CORR[category][label]` is the desired element.
    - `Sorter.handle_orchestra()` is now `Sorter.is_artist_orchestra()` and correctly returns a `bool` as per typing.

## [0.2.1] - 2020-12-17
### Fixed
- Issue #1:
    - If a track lacks an album tag, it will correctly be placed in the next possible tag: the artist tag (group artists).
    - Suffixes like `', Jr.'` can now coexist with a list of artists, as the comma is swapped with an underscore pre-split and swapped back post-split.
- Issue #2:
    - Disc numbers will default to `1` if they are somehow missing or zeroed. Users will be alerted to this change.
    - Missing track numbers can't be fixed, but the user will still be alerted.

## [0.2.0] - 2020-10-31
### Changed
- Forget the CSV functionality. It only hindered moving over tracks accurately. I thought they could be used as a sort of failsafe, but they actually increased complexity. Everything anyone needs to move files is already present within the ID3 metadata of each MP3 file. Some of the data is absent for some reason (including artists) but overall the effort is tremendously effective.

## [0.1.0] - 2020-10-31
### Added
- Initial version

[sorter.py]: sorter/sorter.py
