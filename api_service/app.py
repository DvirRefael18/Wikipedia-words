from typing import Dict, List

import re
import logging
import requests
import wikipedia
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup


BASE_URL = "https://en.wikipedia.org/w/api.php"
WIKI_ARTICLES_DAILY: int = 10
QUERY_DELIMITER: str = ' '
LISTEN_IP = "0.0.0.0"
TERM = 'term'
PORT = 5000
CACHE = {}


logging.basicConfig(filename='./logs/app.log', filemode='w', format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

# Flask framework
app = Flask(__name__)


# Function that returns error logs
def status_code_errors(req):
    return logging.error(f"Error: Failed to get random article. status code:{req.status_code}")


# Fetching articles from wikipedia
@app.route("/fetch_articles")
def fetch_articles():
    i = 0

    # Creating a list, for logging information for each day.
    # the new urls list, contains 10 articles for each day.
    new_urls = []

    # Fetching 10 articles each day.
    while i < WIKI_ARTICLES_DAILY:
        logging.info(f"Trying to get random article from wikipedia URL.")
        try:
            random_url_response = requests.get(
                "https://en.wikipedia.org/wiki/Special:Random")
            logging.info(
                f"Get random url from wikipedia, status code: {random_url_response.status_code}")
        except Exception:
            if random_url_response:
                status_code_errors(random_url_response)
            exit(1)

        # Getting from the response object the URL.
        url_link = random_url_response.url
        logging.info(f"Got {url_link} article from wikipedia.")

        # Checking if the URL not in the cache already. if yes, continue to the next iteration.
        if url_link not in CACHE:
            soup = BeautifulSoup(random_url_response.content, "html.parser")

            # Getting the title of each url. the title will help me to find the specific id of each url.
            first_heading = soup.find(class_="firstHeading")
            if not first_heading:
                logging.error(
                    "Error while trying to parse HTML tag named 'firstHeading' was not found, Exit Program!")
                exit(1)
            title = first_heading.text

            # The schema of the wikipedia.
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": title
            }
            try:
                # This GET request, is to get the page id of the url.
                response = requests.get(url=BASE_URL, params=params)
                logging.info("Trying to get article id from wikipedia URL.")
            except Exception:
                logging.error(
                    f"Error while trying to get article id from wikipedia url, Exit Program!.")
                exit(1)

            data = response.json()
            # Creating a cache. each key in the cache is the URL, and for each
            # URL, the values are the page id of the specipic url, and also
            # the empty words object.
            if data['query']['search'][0]['title'] == title:
                CACHE[url_link] = {"page_id": data['query']
                                   ['search'][0]['pageid'], "words": {}}
                new_urls.append(url_link)
            i += 1

    return jsonify({"results": new_urls})


# search words function, is the function for the api request from the user.
# after calling the api, the result should be an array of objects, s.t each object contains,
# the url names, and the words in the term (if all words was shown in the specipic url).
@app.route("/api/search/")
def search_words():
    # Creating a list of all the words in term.
    args: Dict[str, str] = request.args.to_dict()
    logging.info("Creating list of words by the term in the given API.")
    term_words: List = []
    if query := args.get(TERM):
        term_words = query.lower().split(QUERY_DELIMITER)
    if len(term_words) == 0:
        logging.error("No words founded in term.")

    # Creating a list for the final result.
    results: List = []
    logging.info("Check if given words, already exists in CACHE")

    # Check if the url in the cache.
    for url in CACHE:
        cache_words = CACHE[url]["words"]
        words_not_in_cache = []

        # For each words that was in the term, check if the word in the cache.
        # if not, append the word inside.
        for word in term_words:
            if word not in cache_words:
                words_not_in_cache.append(word)
        if len(words_not_in_cache) > 0:
            try:
                # Getting the text from wikipedia url.
                text = wikipedia.page(pageid=CACHE[url]["page_id"])
            except Exception as e:
                logging.error("Cannot found wikipedia page id. Exit Program!")
                exit(1)

            # Getting the content - the assumption, is that the word needs to be showen in the whole text.
            text = text.content
            text = re.sub(r'==.*?==+,-!', '',
                          text).replace('\n', '').split(" ")

            # for the words, that was not been in the cache, and hence needs to be find in the content.
            for word in words_not_in_cache:
                for word_in_article in text:

                    # Lower because its case insensitive.
                    lower_word = word_in_article.lower()
                    if lower_word == word:
                        if lower_word not in cache_words:
                            cache_words[word] = 1
                        else:
                            cache_words[word] += 1

        occ = 0
        # Using set to check if all the words that was in the term, is in the cache.
        # if yes, Im counting the occurences of the words.
        is_subset = set(term_words).issubset(set(cache_words.keys()))
        if is_subset:
            for word in term_words:
                occ += cache_words[word]
            results.append({"article_url": url, "occurrences": occ})

    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(port=PORT, host=LISTEN_IP)
