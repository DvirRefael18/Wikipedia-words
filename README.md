# Words In Wikipedia Articles

The main task of this program, is to fetch every day
10 random, and unique articles from wikipedia.
The user can send a call to an api, with a term, and the check if the words that includes in the term, are in the articles. if all the words that in the term, are in the article, then the article URL, and the number of occurences of the total words, should be return.

========

# About the Docker:

The enviorment is splited into 2 containers:

1. schedule_service:
   - Include the Main, which set to happen every day.
     Each iteration, will call the api of the other container, and fetch wikipedia articles.
     Only the main thread fetch the data.
2. api_service:
   - Flask application, that has 2 main function.
     a. the first function, "def fetch_articles():"
     will fetch 10 random articles from wikipedia.
     b. "def search_words():", will search words, in the article, by call of the user to this api:
     "/api/search?term=nEw%20York%20city%20design".
     The Term, includes the words, that needs to be found in the articles.
   - To speed up the searching, i created a local CACHE,
     that includes the urls, and the words that already
     found before.

========

# Setup

instructions:

    Each container, includes requirments.txt, that
    holds all the imports for the program.
    Thus, the Only steps to set up the the enviorments are:

    1. Create a Log folder that includes 2 files:
        a. app.log
        b. schedule.log
    2. Make sure that PORT 5000 is available.
    3. To see the solution in a better way, try to use
       POSTMAN.

    4. open CMD, and make sure that you have docker on
       your computer.
        $ docker

       after settting the enviorment, and the docker is on, run the docker in this simple way:
       $ docker-compose build
       $ docker-compose up

       To check that both the containers are up with succses:
       $ docker ps
       and look if you see two containers.

    s.n: make sure that you don't run any other      continers before by writing this command:
        $ docker-compose down

========
