Project 2: IMDB Software of Hollywood Actors and Actresses
In this project, it is needed to create a user-friendly software that stores and extracts information about the top
50 popular Hollywood actor and actresses http://www.imdb.com/list/ls053501318/.
IMDB software should provide following functionality:
1. List of all available actors and actresses
2. About the actor/actresses
3. All time movie names and years
4. Awards to actor/actresses in different years
5. Movie genre of actor/actresses
6. Average rating of their movies (overall and each year)
7. Top 5 movies, their respective years and genre

This project contains two scripts:
-	webscraping.py – the script for webscraping and saving data from imdb website into the database
-	app.py – the web application script to run user-friendly interface.

Modules that should be installed:
- cryptography
- Flask-MySQL
- mysql-connector
- flask
- webdriver_manager
- selenium
- webdriver
- pandas
- beautifulsoup4
- requests
- json

First, user should change in webscraping.py line 81, line 90 and in app.py line 11 password to mysql database if they
have password different from "root".
Next, user should run webscraping.py script to get all necessary data from website and to store it in database. It can
take several hours to complete.
After finishing webscraping.py all data is stored in MySQL so user can start the app.py. To do that user should type
"flask --app app run" in terminal. After that click on link " http://127.0.0.1:5000" in the terminal or paste it in
web-browser. That will lead to the main page of application with all actresses/actors as links. After clicking on
certain actor, personal profile will be opened with actor’s biography, top 3 genres, top 5 movies and links to
filmography, awards and all actors page. After clicking on filmography link the page with all actor’s films will appear.
It also contains links to average ratings, back to actor and to all actors. If user clicks on the film, it will redirect
to film’s imdb page. After clicking on rating page, it will show average rating of all actor`s films and average rating
of each year respectively (and, of course, links to current actor and to all actors). If user goes back to actor`s
personal page and clicks on awards, awards page will appear. It also contains links to go back to current actor or to
all actors.