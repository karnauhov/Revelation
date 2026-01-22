import requests
import time

BASE_URL = "https://biblehub.com/greek/{}.htm"
START = 1
END = 5624

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BibleHubParser/1.0)"
}

TIMEOUT = 10          # seconds
DELAY = 0.3           # delay between requests


def main():
    not_found = 0

    for i in range(START, END + 1):
        page_name = f"{i}.htm"
        url = BASE_URL.format(i)

        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

            if response.status_code != 200:
                print(f"{page_name} — HTTP {response.status_code}")
                not_found += 1
            else:
                if "Occurrence" not in response.text:
                    print(page_name)
                    not_found += 1

        except requests.exceptions.RequestException as e:
            print(f"{page_name} — request error: {e}")
            not_found += 1

        time.sleep(DELAY)

    print(f"\nTotal pages without 'Occurrence': {not_found}")


if __name__ == "__main__":
    main()
