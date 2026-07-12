from extract import extract
from transform import transform
from validation import validate
from load import load

from config.logger import logger


def main():

    logger.info("Extract")

    soup = extract()

    logger.info("Transform")

    df = transform(soup)

    df = validate(df)

    logger.info(f"{len(df)} records")

    load(df)

    logger.info("Pipeline selesai")


if __name__ == "__main__":

    main()