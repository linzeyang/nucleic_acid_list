import csv
from datetime import datetime
from http import HTTPStatus
import logging
from pathlib import Path
from typing import List

from git import Repo
from requests_html import HTMLSession


URL = "https://hr.cs.mfa.gov.cn/help_two/help-two/gj.html"
FILENAME = "country_list.csv"


def initialize_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel("DEBUG")
    fh = logging.FileHandler(Path(__file__).parent / "history.log")
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(fh)
    return logger


def main():
    logger.info("\n***** Start *****")

    response = fetch_source()

    data = [
        [item.full_text for item in line.find("li")]
        for line in response.html.find(
            "#englishbox > div.cotent > div.table > div.englishlist > ul.tableli",
        )
    ]

    if not data:
        logger.warning("\n----- No valid data found -----")
        exit(0)

    update_local_csv(data=data)
    update_repo()


def fetch_source():
    response = HTMLSession().get(URL)

    if response.status_code != HTTPStatus.OK:
        logger.error(f"\n+++++ Response code: {response.status_code} . Exiting +++++")
        exit(0)

    logger.info("\n----- Source fetched -----")

    try:
        response.html.render(retries=20, timeout=30)
    except Exception as e:
        logger.error(f"\n+++++ Failed to render: {str(e)} +++++")
        exit(1)
    else:
        return response


def update_local_csv(data: List[list]):
    p = Path(__file__).parent / FILENAME

    with p.open(mode="r") as file:
        reader = csv.reader(file)
        existing_data = [line for line in reader]

    if data == existing_data:
        logger.info("\n----- No change found on source site -----")
        exit(0)

    logger.info("\n----- Changes found on source site -----")

    with p.open(mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)


def update_repo():
    repo = Repo(path=Path(__file__).parent)

    if not repo.is_dirty():
        logger.warning("\n+++++ Nothing to commit locally +++++")
        exit(0)

    repo.index.add(
        items=[FILENAME,]
    )
    repo.index.commit(message=f"Update csv at {datetime.utcnow()}")
    repo.remote().push()

    logger.info("\n----- Pushed to upstream -----")


if __name__ == "__main__":
    logger = initialize_logger()
    main()
