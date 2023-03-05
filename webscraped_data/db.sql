use imdb;

select id_actor, name_actor, bio_actor
from actors;

select name_award, year_award, outcome_award, description_award, film_award
from  awards aw
inner join actors ac using (id_actor)
where id_actor = 1;

select name_film, year_film, rating_film 
from films
inner join actors ac using (id_actor)
where id_actor = 1;

select name_film, year_film, rating_film, name_genre
from films
inner join actors ac using (id_actor)
inner join genres g using (id_film)
where id_actor = 1;

select name_genre, count(*) as Genre_count
from films
inner join actors ac using (id_actor)
inner join genres g using (id_film)
where id_actor = 1
group by g.name_genre
order by Genre_count DESC
#LIMIT 3
;

select name_film, year_film, rating_film 
from films
inner join actors ac using (id_actor)
where id_actor = 1
order by rating_film DESC
LIMIT 5;

select name_film, year_film, rating_film 
from films
inner join actors ac using (id_actor)
where id_actor = 1
order by year_film, rating_film DESC;

select year_film, truncate(avg(rating_film),3)  
from films
inner join actors ac using (id_actor)
where id_actor = 1
and year_film like '____'
and year_film not like '-'
and rating_film not like '-'
group by year_film
order by year_film DESC;

select name_actor,truncate(avg(rating_film),3)  
from films
inner join actors ac using (id_actor)
where id_actor = 1
and rating_film not like '-';