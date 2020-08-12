import csv
from http import HTTPStatus
from pathlib import Path

from requests_html import HTMLSession


URL = "https://hr.cs.mfa.gov.cn/help_two/help-two/gj.html"


def main():
    session = HTMLSession()

    print("Start")

    response = session.get(URL)

    if response.status_code != HTTPStatus.OK:
        print(f"Response code: {response.status_code}")
        exit(0)

    print("Source fetched")

    try:
        response.html.render(retries=20, timeout=30)
    except Exception as e:
        print(f"Failed to render: {str(e)}")
        exit(1)

    data = [
        [item.full_text for item in line.find("li")]
        for line in response.html.find(
            "#englishbox > div.cotent > div.table > div.englishlist > ul.tableli",
        )
    ]

    if not data:
        print("No valid data found")
        exit(0)

    p = Path("country_list.csv")

    with p.open(mode="r") as file:
        reader = csv.reader(file)
        existing_data = [line for line in reader]

    if data == existing_data:
        print("No change found")
        exit(0)

    with p.open(mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)

    exit(0)


if __name__ == "__main__":
    main()
