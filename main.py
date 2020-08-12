import csv
from datetime import datetime
from http import HTTPStatus
import logging
from pathlib import Path

from git import Repo
from requests_html import HTMLSession


URL = "https://hr.cs.mfa.gov.cn/help_two/help-two/gj.html"
FILENAME = "country_list.csv"


def main():
    session = HTMLSession()

    logger.info("Start")

    response = session.get(URL)

    if response.status_code != HTTPStatus.OK:
        print(f"Response code: {response.status_code}")
        exit(0)

    logger.info("Source fetched")

    try:
        response.html.render(retries=20, timeout=30)
    except Exception as e:
        logger.error(f"Failed to render: {str(e)}")
        exit(1)

    data = [
        [item.full_text for item in line.find("li")]
        for line in response.html.find(
            "#englishbox > div.cotent > div.table > div.englishlist > ul.tableli",
        )
    ]

    if not data:
        logger.warning("No valid data found")
        exit(0)

    p = Path(__file__).parent / FILENAME

    with p.open(mode="r") as file:
        reader = csv.reader(file)
        existing_data = [line for line in reader]

    if data == existing_data:
        logger.info("No change found on source site")
        exit(0)

    with p.open(mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)

    repo = Repo(path=Path(__file__).parent)

    if not repo.is_dirty():
        logger.warning("Nothing to commit locally")
        exit(0)

    repo.index.add(items=[FILENAME,])
    repo.index.commit(message=f"Update csv at {datetime.utcnow()}")
    repo.remote().push()

    exit(0)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel("DEBUG")
    fh = logging.FileHandler(Path(__file__).parent / "history.log")
    fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)
    main()
