from sorter import config
from sorter import sorter


if __name__ == '__main__':
    s = sorter.Sorter()
    s.sort()
    if not s.does_file_count_match():
        config.LOGGER.warning('The file count did not match pre-sort.')
        config.LOGGER.warning('Please manually compare with your archive.')
    else:
        config.LOGGER.info(
            'The current file count successfully matched pre-sort.'
            )
