#2lazy

import logging

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def setup_formatter(logger):
    logger.setFormatter(formatter)
