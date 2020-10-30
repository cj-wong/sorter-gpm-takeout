import json
import logging
import logging.handlers
from pathlib import Path


_LOGGER_NAME = 'sorter-gpm'

LOGGER = logging.getLogger(_LOGGER_NAME)
LOGGER.setLevel(logging.DEBUG)

_FH = logging.handlers.RotatingFileHandler(
    f'{_LOGGER_NAME}.log',
    maxBytes=40960,
    backupCount=5,
    )
_FH.setLevel(logging.DEBUG)

_CH = logging.StreamHandler()
_CH.setLevel(logging.WARNING)

FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
_FH.setFormatter(FORMATTER)
_CH.setFormatter(FORMATTER)

LOGGER.addHandler(_FH)
LOGGER.addHandler(_CH)


_CONFIG_LOAD_ERRORS = (
    FileNotFoundError,
    KeyError,
    TypeError,
    ValueError,
    json.decoder.JSONDecodeError,
    )


try:
    with open('config.json', 'r') as f:
        CONFIG = json.load(f)
    FMT = CONFIG['format']
    _TAKEOUT = Path(CONFIG['takeout_dir']).expanduser()
    TRACKS = _TAKEOUT / 'Google Play Music' / 'Tracks'
    DEST = Path(CONFIG['dest_dir']).expanduser()
except _CONFIG_LOAD_ERRORS as e:
    LOGGER.error('config.json doesn\'t exist or is malformed.')
    LOGGER.error(f'More information: {e}')
    raise e
