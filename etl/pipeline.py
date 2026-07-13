from etl.extract import extract
from etl.transform import transform
from etl.load import load
from etl.validation import validate

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