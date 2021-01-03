# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
