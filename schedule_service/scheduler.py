import requests
import time
import logging

API_SERVICE_HOSTNAME = 'api-service'
TOTAL_URLS = 10
PORT = 5000
WAITING_TIME = 60 * 60 * 24


logging.basicConfig(filename='./logs/schedule.log', filemode='w', format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


def main():

    # As long the program is running, without issues.
    while True:
        try:
            # Calling the fetch articles route in api-service container,
            # To fetch 10 URL'S.
            response = requests.get(
                f"http://{API_SERVICE_HOSTNAME}:{PORT}/fetch_articles")
            new_urls = response.json()["results"]
            logging.info(
                f"Fetched total {TOTAL_URLS} new urls: {new_urls}")
        except Exception:
            logging.error(
                "Failed fetching urls from wikipedia, Exit program!", exc_info=True)

        # Happend every 24 hours.
        time.sleep(WAITING_TIME)


if __name__ == "__main__":
    main()
