# import the library used to query a website
import requests
# import the Beautiful soup functions to parse the data returned from the website
from bs4 import BeautifulSoup
# import pandas to convert list to data frame
import pandas as pd
# import json to find json-formatted data in data from the website
import json
# import libraries to work with MySQL DBMS
import mysql.connector
from mysql.connector import Error
# import selenium to open buttons "show more"
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
# import time to make program wait where it is needed
import time


#
# DATABASE
#

# function to create connection to the whole database system
def create_connection(host_name, user_name, user_password):
    con = None
    try:
        con = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return con


# function to create new database
def create_database(con, query):
    cursor = con.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


# function to create connection to specific database with name db_name in the system
def create_db_connection(host_name, user_name, user_password, db_name):
    con = None
    try:
        con = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MYSQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return con


# function to execute queries with catching errors
def execute_query(con, query):
    cursor = con.cursor()
    try:
        cursor.execute(query)  # pass our Query through
        con.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


#
# CREATE DATABASE
#

# make connection to MySQL
connection = create_connection("localhost", "root", "root")
# query for creating new database where data of this program will be stored
create_database_query = "CREATE DATABASE imdb"
# execute query
create_database(connection, create_database_query)

#
# CREATE CONNECTION FOR TABLES
#
connection_db = create_db_connection("localhost", "root", "root", "imdb")

#
# SCRAPE ACTORS` LINKS FROM LIST OF 50 ACTORS AND ACTRESSES
#

# specify the url
imdb = "https://www.imdb.com/list/ls053501318/"
# Query the website and return the html to the variable 'page'
page = requests.get(imdb)
# Parse the html in the 'page' variable, and store it in Beautiful Soup format
soup = BeautifulSoup(page.text, 'html.parser')

# find script in html with json list of actresses and actors
res = soup.find('script', type='application/ld+json').text.strip()
# find json data in that script
json_data = json.loads(res)
# blank list for urls of actors and actresses
LINKS = []
# find all urls in json data
for item in json_data['about']['itemListElement']:
    LINKS.append('https://www.imdb.com' + item['url'])

#
#   #ACTORS BIO
#

# list for actresses and actors names
ACTOR_ESS = []
# list for biographies for actors and actresses
BIO = []
# headers that are needed for accessing websites, because without them, it gives 403 error
head = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/108.0.0.0 Mobile Safari/537.36'}
# for each actress/actor
for link in LINKS:
    # get their personal page
    page_n = requests.get(link, headers=head)
    # get html of the page
    soup_n = BeautifulSoup(page_n.text, 'html.parser')
    # find name of actor/actress
    ACTOR_ESS.append(soup_n.find('title').text.replace(' - IMDb', ''))
    # link of actress/actor biography
    imdb_bio = link + 'bio/'
    # get bio page
    page_bio = requests.get(imdb_bio, headers=head)
    # get html of the page
    soup_bio = BeautifulSoup(page_bio.text, 'html.parser')
    # find biography of actor/actress
    BIO.append(soup_bio.findAll('div', class_="col-xs-12")[-1].text.strip())

# create dataframe for actresses/actors information
df_actors = pd.DataFrame()
# column for their names
df_actors['ACTOR_ESS'] = ACTOR_ESS
# column for their biography
df_actors['BIO'] = BIO
# column for links of their personal pages
df_actors['LINK'] = LINKS

#
# CREATE ACTORS TABLE
#

create_actors_table = """
CREATE TABLE IF NOT EXISTS actors (
  id_actor INTEGER PRIMARY KEY AUTO_INCREMENT,
  name_actor TEXT,
  link_actor TEXT,
  bio_actor TEXT
);
"""
execute_query(connection_db, create_actors_table)

#
# INSERT ACTORS
#
# for passing data to database dataframe is merged to list of tuples
actors_list = []
for row in df_actors.to_numpy():
    actors_list.append(tuple(row))
# get cursor
mycursor = connection_db.cursor()
# query for inserting actors data where %s means additional info that is got from list of tuples
sql = """INSERT INTO imdb.actors (name_actor, bio_actor, link_actor) VALUES (%s, %s, %s)"""
# execute query with data from actors_list
mycursor.executemany(sql, actors_list)
# commit changes to database
connection_db.commit()
# print in log to be sure that insertion is correct
print(mycursor.rowcount, "were inserted.")

#
# AWARDS
#

# lists for information about awards
ACTOR_ID = []
AWARD_NAME = []
YEAR = []
OUTCOMES = []
DESCRIPTION = []
FILMS = []
year = ''
outcome = ''
description = ''
film = ''
# number for award names
num = 0
# number for id of actor/-ess that will be foreign keys in database table
N = 1
# for each actress/actor
for link in LINKS:
    # link for their award page
    imdb_awards = link + 'awards/'
    # get the page
    page_awards = requests.get(imdb_awards)
    # get html of the page
    soup_awards = BeautifulSoup(page_awards.text, 'html.parser')
    # find all tables of awards
    awards = soup_awards.findAll('table', class_='awards')
    # find names of all awards
    awards_n = soup_awards.findAll('h3')[1:-2]
    # for each award
    for award in awards:
        # for each nomination for this award
        for row in award.find_all("tr"):
            # add id of current actress/actor
            ACTOR_ID.append(N)
            # name of current award
            AWARD_NAME.append(awards_n[num].text)
            # year of nomination. for some years actors have several nominations and year is written only for one of
            # them. so for next awards that don`t have year written will be stated previous year
            if row.find('td', class_="award_year") is not None:
                year = row.find('td', class_="award_year").text.strip()
            YEAR.append(year)
            # the same situation with award outcome as with the year
            if row.find('td', class_="award_outcome") is not None:
                outcome = row.find('td', class_="award_outcome").text.strip().replace('\n', ' - ')
            OUTCOMES.append(outcome)
            # find award description
            if row.find('td', class_="award_description") is not None:
                description = row.find('td', class_="award_description").text.strip()[
                              :row.find('td', class_="award_description").text.strip().find('\n')]
            DESCRIPTION.append(description)
            # find award film and it's year
            if row.find('td', class_="award_description").find('a') is not None and \
                    row.find('td', class_="award_description").find('span') is not None:
                film = row.find('td', class_="award_description").find('a').text.strip() + \
                       ' ' + row.find('td', class_="award_description").find('span').text.strip()
            else:
                film = ''
            FILMS.append(film)
        # go to the next award name
        num = num + 1
    # set first award name for next actress/actor
    num = 0
    # go to next actor/-ess id
    N = N + 1

# create dataframe for award information
df_awards = pd.DataFrame()
# column for their actress's/actors' id
df_awards['ACTOR_ID'] = ACTOR_ID
# column for award name
df_awards['AWARD_NAME'] = AWARD_NAME
# column for award year
df_awards['YEAR'] = YEAR
# column for award outcome
df_awards['OUTCOME'] = OUTCOMES
# column for award description
df_awards['DESCRIPTION'] = DESCRIPTION
# column for award film
df_awards['FILM'] = FILMS

#
# CREATE AWARDS TABLE
#

create_awards_table = """
CREATE TABLE IF NOT EXISTS awards (
  id_award INTEGER PRIMARY KEY AUTO_INCREMENT,
  id_actor INTEGER NOT NULL,
  name_award TEXT,
  year_award INTEGER,
  outcome_award TEXT,
  description_award TEXT,
  film_award TEXT,
  # Because table of actors already exists we can make reference using actors` ids
  constraint `actor_award` foreign key (`id_actor`) references `actors` (`id_actor`) 
);
"""
# execute creation of awards table
execute_query(connection_db, create_awards_table)

#
# INSERT AWARDS
#
# for passing data to database dataframe is merged to list of tuples
awards_list = []
for row in df_awards.to_numpy():
    awards_list.append(tuple(row))
# get cursor
mycursor = connection_db.cursor()
# query for inserting awards data where %s means additional info that is got from list of tuples
sql = """INSERT INTO awards (id_actor, name_award, year_award, outcome_award, description_award, film_award) VALUES (
%s, %s, %s, %s, %s, %s) """
# execute query with data from awards_list
mycursor.executemany(sql, awards_list)
# commit changes to database
connection_db.commit()
# print in log to be sure that insertion is correct
print(mycursor.rowcount, "were inserted.")

#
# FILMOGRAPHY
#

# headers that are needed for accessing websites, because without them, it gives 403 error
head = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/108.0.0.0 Mobile Safari/537.36'}
# blank lists for information about films
FILM_NAME = []
FILM_YEAR = []
RATING = []
FILM_LINK = []
ACTOR_ID = []
# id of actor for referencing in database
actor = 1
# for each actress/actor
for link in LINKS:
    # start webdriver to open hidden parst of filmography
    driver = webdriver.Chrome("C:\\chromedriver.exe")
    # open link of actor
    driver.get(link)
    # find button "show more"
    button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='nm-flmg-all-accordion-expander'][role='button']")
    button.send_keys(Keys.SPACE)
    # click the button and show hidden elements
    driver.execute_script("arguments[0].scrollIntoView();", button)
    driver.execute_script("arguments[0].click();", button)
    # provide some delay here
    time.sleep(2)
    # get html of page with opened hidden elements
    soup_f = BeautifulSoup(driver.page_source)
    # list for all films` links that are on the page
    film_links = []
    # append links to list in right format for future webscraping
    for lili in soup_f.findAll('li', class_="ipc-metadata-list-summary-item"):
        film_links.append('https://www.imdb.com' + lili.find('a')['href'])
    # for each film in result list
    for film_link in film_links:
        # append id of current actor
        ACTOR_ID.append(actor)
        # append link to the film
        FILM_LINK.append(film_link)
        # request page from link
        page_ff = requests.get(film_link, headers=head)
        # get html of the page
        soup_ff = BeautifulSoup(page_ff.text, 'html.parser')
        # find name of the film
        FILM_NAME.append(soup_ff.find('h1').text)
        # if film does not have release year append "-" else append year of film
        if soup_ff.find('div', class_="sc-80d4314-2 iJtmbR").find("span") is None:
            FILM_YEAR.append('-')
        else:
            FILM_YEAR.append(soup_ff.find('div', class_="sc-80d4314-2 iJtmbR").find("span").text)
        # if film does is not released yet and does not have rating append "-" else append rating of film
        if soup_ff.find('span', class_="sc-7ab21ed2-1 jGRxWM") is None:
            RATING.append('-')
        else:
            RATING.append(soup_ff.find('span', class_="sc-7ab21ed2-1 jGRxWM").text)
    # go to id of next actor/actress
    actor = actor + 1

# create dataframe for films information
df_films = pd.DataFrame()
# column for their names
df_films['FILM_NAME'] = FILM_NAME
# column for their year
df_films['FILM_YEAR'] = FILM_YEAR
# column for links of their rating
df_films['RATING'] = RATING
# column for films` links
df_films['FILM_LINK'] = FILM_LINK
# column for id of actor who plays in this film
df_films['ACTOR_ID'] = ACTOR_ID

#
# CREATE FILMS TABLE
#
# query for creation of films table
create_films_table = """
CREATE TABLE IF NOT EXISTS films (
  id_film INTEGER PRIMARY KEY AUTO_INCREMENT,
  id_actor INTEGER NOT NULL,
  name_film TEXT,
  year_film TEXT,
  rating_film TEXT,
  link_film TEXT,
  # Because table of actors already exists we can make reference using actors` ids
  constraint `actor_film` foreign key (`id_actor`) references `actors` (`id_actor`)
);
"""
execute_query(connection_db, create_films_table)

#
# INSERT FILMS
#
# for passing data to database dataframe is merged to list of tuples
films_list = []
for row in df_films.to_numpy():
    films_list.append(tuple(row))
# get cursor
mycursor = connection_db.cursor()
# query for inserting films data where %s means additional info that is got from list of tuples
sql = """INSERT INTO films (name_film, year_film, rating_film, link_film, id_actor) VALUES (%s, %s, %s, %s, %s)"""
# execute query with data from films_list
mycursor.executemany(sql, films_list)
# commit changes to database
connection_db.commit()
# print in log to be sure that insertion is correct
print(mycursor.rowcount, "were inserted.")

#
# GENRE
#

# headers that are needed for accessing websites, because without them, it gives 403 error
head = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/108.0.0.0 Mobile Safari/537.36'}
# blank lists for info about movie genres, because movies may have more than one
FILM_ID = []
GENRE = []
# id of film for referencing in work with database
film = 1
# for each film
for link in FILM_LINK:
    # get page from link
    page_n = requests.get(link, headers=head)
    # get html of the page
    soup_ff = BeautifulSoup(page_n.text, 'html.parser')
    # find all genres of this film and for each of them
    for genre in soup_ff.findAll('a', class_="sc-16ede01-3 bYNgQ ipc-chip ipc-chip--on-baseAlt"):
        # append id of the film
        FILM_ID.append(film)
        # append genre name
        GENRE.append(genre.text)
    # go to id of next film
    film = film + 1
# create dataframe for genres
df_genres = pd.DataFrame()
# column for their names
df_genres['GENRE'] = GENRE
# column for their film's id
df_genres['FILM_ID'] = FILM_ID

#
# CREATE GENRES TABLE
#

create_genre_table = """
CREATE TABLE IF NOT EXISTS genres (
  id_genre INTEGER PRIMARY KEY AUTO_INCREMENT,
  id_film INTEGER NOT NULL,
  name_genre TEXT,
  constraint `film_genre` foreign key (`id_film`) references `films` (`id_film`)
);
"""
execute_query(connection_db, create_genre_table)

#
# INSERT GENRES
#
# for passing data to database dataframe is merged to list of tuples
genre_list = []
for row in df_genres.to_numpy():
    genre_list.append(tuple(row))
# get cursor
mycursor = connection_db.cursor()
# query for inserting films data where %s means additional info that is got from list of tuples
sql = """INSERT INTO genres (name_genre, id_film) VALUES (%s, %s)"""
# execute query with data from films_list
mycursor.executemany(sql, genre_list)
# commit changes to database
connection_db.commit()
# print in log to be sure that insertion is correct
print(mycursor.rowcount, "were inserted.")

#
# WEBSCRAPING PART IS OVER. All data is stored in the database
#
