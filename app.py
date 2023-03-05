# import Flask library to work with webserver
from flask import Flask
# import flask library for working with MySQL DBMS. It may show MySQL as error - just ignore that, it will work properly
from flaskext.mysql import MySQL

# start app
app = Flask(__name__)
# input keys for connecting to database
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'imdb'
# connect to database
mysql = MySQL(app)

# function for launching main page with all 50 actresses/actors
@app.route("/")
def hello_world():
    # Creating a connection cursor
    cursor = mysql.get_db().cursor()
    # select ids and names of all actresses/actors
    cursor.execute(" SELECT id_actor, name_actor FROM actors")
    result = cursor.fetchall()
    # close database connection
    cursor.close()
    # write header in html
    html = "<h1>Top 50 Actors</h1>\n"
    # write all actresses/actors names as links to their personal pages in this program
    for actor in result:
        html = html + "<a href = '/" + str(actor[0]) + "'>" + actor[1] + "</a><p></p>"
    # show the resulting html
    return html


# function for launching main page of certain actress/actor
@app.route('/<int:id_actor>')
def show_actor(id_actor):
    # Creating a connection cursor
    cursor = mysql.get_db().cursor()
    # get data about name of current actor from database
    cursor.execute(" select name_actor, bio_actor from actors where id_actor = %s", id_actor)
    actor = cursor.fetchall()
    # select from database genres of actress/actor with their amount in filmography and sort them descending
    # so the most frequent genres are on the top
    cursor.execute("select name_genre, count(*) as Genre_count from films inner join actors ac "
                   "using (id_actor) inner join genres g using (id_film) where id_actor = %s "
                   "group by g.name_genre order by Genre_count DESC ", id_actor)
    genres = cursor.fetchall()
    # select 5 first films of current actress with the highest rating
    cursor.execute("select name_film, year_film, rating_film, id_film from films inner join "
                   "actors ac using (id_actor)where id_actor = %s order by rating_film DESC LIMIT 5", id_actor)
    top_films = cursor.fetchall()
    # write in html header, link to all actors, to actor's Filmography and to awards
    html = "<h1>" + actor[0][0] + "</h1>\n" + "<a href = '/'> Go back to all actors </a><p></p><a href = '/filmography/" \
           + str(id_actor) + "'> Go to actor's Filmography</a><p></p><a href = '/awards/" + str(id_actor) + \
           "'> Go to awards </a><p>" + actor[0][1] + "</p>"
    # write in html top 3 genres of actors with their count of movies
    html = html + "<h3>Top 3 genres of actor:</h3><p>" + genres[0][0] + " (" + str(genres[0][1]) + " movies), " + \
           genres[1][0] + " (" + str(genres[1][1]) + " movies), " + genres[2][0] + " (" + str(genres[2][1]) + \
           " movies)</p><h3>Top 5 actors movies</h3><table><tr><th>Film</th><th>Year</th><th>Rating</th><th>Genre</th></tr>"
    # for each film from top 5 of this actor
    for movie in top_films:
        # write info about film into table row
        html = html + "<tr><td>" + movie[0] + "</td><td>" + str(movie[1]) + "</td><td>" + str(movie[2]) + "</td><td>"
        # select from database all genres of current film
        cursor.execute("select name_genre from films inner join genres g using (id_film) where id_film = %s", movie[3])
        genres = cursor.fetchall()
        # print all genres of film into one table cell
        for genre in genres:
            html = html + genre[0] + " "
        # close table cell and ow
        html = html + "</td></tr>"
    # close database connection
    cursor.close()
    # close table
    html = html + "</table>"
    # show the resulting html
    return html


# function for launching filmography page of certain actress/actor
@app.route('/filmography/<int:id_actor>')
def show_actors_filmography(id_actor):
    # Creating a connection cursor
    cursor = mysql.get_db().cursor()
    # get data about name of current actor from database
    cursor.execute("select name_actor from actors where id_actor = %s", id_actor)
    actor = cursor.fetchall()
    # select all films of this actor
    cursor.execute("select link_film, name_film, year_film, rating_film, id_film from films "
                   "inner join actors ac using (id_actor) where id_actor = %s", id_actor)
    films = cursor.fetchall()
    # write in html header, links to go to all actors, current actor and to actor's average rating
    html = "<h1>Filmography of " + actor[0][0] + "</h1>\n" + "<a href = '/'> Go back to all actors </a><p></p><a href = '/" \
           + str(id_actor) + "'> Go back to " + actor[0][0] + "</a><p></p><a href = '/rating/" + str(id_actor)\
           + "'> Go to actor's average rating </a>"
    # write table for films and headers for it
    html = html + "<table><tr><th>Film</th><th>Year</th><th>Rating</th><th>Genre</th></tr>"
    # for each film of current actor
    for film in films:
        # write info about film into table row
        html = html + "<tr><td><a href = '" + str(film[0]) + "'>" + film[1] + "</a></td><td>" + str(
            film[2]) + "</td><td>" + str(film[3]) + "</td><td>"
        # select from database genres of current film
        cursor.execute("select name_genre from films inner join genres g using (id_film) where id_film = %s", film[4])
        genres = cursor.fetchall()
        # print all film`s genres in one table cell
        for genre in genres :
            html = html + genre[0] + " "
        # close table cell and row
        html = html + "</td></tr>"
    # close table
    html = html + "</table>"
    # close database connection
    cursor.close()
    # show the resulting html
    return html


# function for launching awards page of certain actress/actor
@app.route('/awards/<int:id_actor>')
def show_actors_awards(id_actor):
    # Creating a connection cursor
    cursor = mysql.get_db().cursor()
    # get data about name of current actor from database
    cursor.execute("select name_actor from actors where id_actor = %s", id_actor)
    actor = cursor.fetchall()
    # select from database data about awards of current actor
    cursor.execute("select name_award, year_award, outcome_award, description_award, film_award from awards "
                   "aw inner join actors ac using (id_actor) where id_actor = %s order by year_award DESC", id_actor)
    awards = cursor.fetchall()
    # close database connection
    cursor.close()
    # write in html header, links to go back to all actors and to current actor
    html = "<h1>Awards of " + actor[0][0] + "</h1>\n" + "<a href = '/'> Go back to all actors </a><p></p><a href = '/" \
           + str(id_actor) + "'> Go back to " + actor[0][0] + "</a>"
    # create awards table and its headers
    html = html + "<table><tr><th>Year</th><th>Award</th><th>Outcome</th><th>Description</th><th>Film</th></tr>"
    #  for each award write its details into table row
    for award in awards:
        html = html + "<tr><td>" + str(award[1]) + "</td><td>" + award[0] + "</td><td>" + str(award[2]) + \
               "</td><td>" + str(award[3]) + "</td><td>" + str(award[4]) + "</td></tr>"
    # close table
    html = html + "</table>"
    # show the resulting html
    return html


# function for launching rating page of certain actress/actor
@app.route('/rating/<int:id_actor>')
def show_actors_avg(id_actor):
    # Creating a connection cursor
    cursor = mysql.get_db().cursor()
    # get data about name of current actor from database
    cursor.execute("select name_actor from actors where id_actor = %s", id_actor)
    actor = cursor.fetchall()
    # select average rating of all films of this actor and round it to 3 symbols after coma
    cursor.execute("select truncate(avg(rating_film),3) from films inner join "
                   "actors ac using (id_actor) where id_actor = %s and rating_film not like '-'", id_actor)
    avg_actor = cursor.fetchall()
    # select average ratings of films of this actor for each year and round them to 3 symbols after coma
    cursor.execute("select year_film, truncate(avg(rating_film),3) from films inner join "
                   "actors ac using (id_actor) where id_actor = %s and year_film like '____' "
                   "and year_film not like '-' and rating_film not like '-' group by year_film order by year_film DESC",
                   id_actor)
    avg_years = cursor.fetchall()
    # close database connection
    cursor.close()
    # make html script for showing title, links to go back to all actors and to current actor,
    # show average rating of all films af actress/actor and header for ratings by years
    html = "<h1>Ratings of " + actor[0][0] + "</h1>\n" + "<a href = '/'> Go back to all actors </a><p></p><a href = '/" \
           + str(id_actor) + "'> Go back to " + actor[0][0] + "</a><h3>Average rating of all movies: " \
           + str(avg_actor[0][0]) + "</h3><h3>Average ratings by years:</h3>"
    # create table for ratings and names of its columns
    html = html + "<table><tr><th>Year</th><th>Rating</th></tr>"
    # for each year write it and its average rating in the table
    for avg in avg_years:
        html = html + "<tr><td>" + str(avg[0]) + "</td><td>" + str(avg[1]) + "</td></tr>"
    # close table
    html = html + "</table>"
    # show the resulting html
    return html
