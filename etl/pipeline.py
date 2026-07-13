from extract import extract
from transform import transform
from validation import validate
from load import load

from config.logger import logger

def main():

    try:

        logger.info("Pipeline started")

        soup = extract()

        df = transform(soup)

        df = validate(df)

        load(df)

        logger.info("Pipeline success")

    except Exception as e:

        logger.exception(e)

        raise