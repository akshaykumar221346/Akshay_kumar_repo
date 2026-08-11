use sakila;
select * from store;
select * from customer;
select * from film;
select * from payment;
-- Display the number of customers in each store.
select count(customer_id) from customer group by store_id;
-- Display the average rental rate for each film rating. Sort the results from highest average rental rate to lowest.
select avg(rental_rate) from film group by rating order by avg(rental_rate) desc;
-- Find all payments where the amount is between $5 and $8.
select payment_id from payment where amount between 5 and 8 ;
-- Display all customers whose first name starts with 'A'.
select first_name from customer where first_name Like 'A%';
-- Find all films whose title contains the word 'LOVE' and sort them alphabetically.
select title from film where title like '%Love%' order by title asc;
-- Display the number of films in each rating category.Include only ratings having more than 180 films.Sort the results by the number of films in descending order.
select count(film_id)from film group by rating having count(film_id)>180 order by count(film_id) desc;

use supply_chain_db