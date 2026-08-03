use sakila;
select * from customer;
select * from film;
-- 1. Get all customers whose first name starts with 'J' and who are active.
select first_name from customer where first_name like 'J%' and active=1;

-- 2. Find all films where the title contains the word 'ACTION' or the description contains 'WAR'.
select title,description from film where title like '%ACTION%' or description like '%WAR%';

-- 3. List all customers whose last name is not 'SMITH' and whose first name ends with 'a'.
select first_name,last_name from customer where last_name !='SMITH' and first_name like '%a';

-- 4. Get all films where the rental rate is greater than 3.0 and the replacement cost is not null.
select rental_rate,replacement_cost from film where rental_rate>3.0 and replacement_cost is not null;

-- 5. Count how many customers exist in each store who have active status = 1.
select count(*),store_id from customer where active=1 group by store_id;

-- 6. Show distinct film ratings available in the film table.
select distinct rating from film;

-- 7. Find the number of films for each rental duration where the average length is more than 100 minutes.
select count(*),avg(length) as avg_length,rental_duration from film group by rental_duration having avg_length>100;

-- 8. List payment dates and total amount paid per date, but only include days where more than 100 payments were made.
select date(payment_date),sum(amount) from payment group by date(payment_date) having count(*)>100;

-- 9. Find customers whose email address is null or ends with '.org'.
select email from customer where email is null or email like '%.org';

-- 10. List all films with rating 'PG' or 'G', and order them by rental rate in descending order.
select rating,rental_rate from film where rating = 'PG' or rating = 'G' order by rental_rate desc;

-- 11. Count how many films exist for each length where the film title starts with 'T' and the count is more than 5.
select length,count(*) from film where title like 'T%' group by length having count(*)>5;

-- 12. List all actors who have appeared in more than 10 films.
select a.actor_id,a.first_name,count(*) as number_of_films from film_actor af inner join actor a on af.actor_id=a.actor_id group by a.actor_id having count(*)>10;

-- 13. Find the top 5 films with the highest rental rates and longest lengths combined, ordering by rental rate first and length second.
select title,length,rental_rate from film order by rental_rate desc,length desc limit 5;

-- 14. Show all customers along with the total number of rentals they have made, ordered from most to least rentals.
SELECT c.customer_id, c.first_name, c.last_name, COUNT(r.rental_id) AS total_rentals FROM customer c LEFT JOIN rental r ON c.customer_id = r.customer_id GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY total_rentals DESC;

-- 15. List the film titles that have never been rented.
select f.title from film f left join inventory i on f.film_id=i.film_id left join rental r on i.inventory_id=r.inventory_id where r.rental_id is null;