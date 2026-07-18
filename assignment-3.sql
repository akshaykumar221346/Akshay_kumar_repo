USE sakila;


/* =========================================================
   QUESTION 1
   Display all customer details who made more than 5 payments.
   ========================================================= */

DELIMITER //

CREATE PROCEDURE GetCustomersWithMoreThanFivePayments()
BEGIN
    SELECT *
    FROM customer
    WHERE customer_id IN (
        SELECT customer_id
        FROM payment
        GROUP BY customer_id
        HAVING COUNT(payment_id) > 5
    );
END //

DELIMITER ;

CALL GetCustomersWithMoreThanFivePayments();


/* =========================================================
   QUESTION 2
   Find actors who acted in more than 10 films.
   ========================================================= */

DELIMITER //

CREATE PROCEDURE GetActorsWithMoreThanTenFilms()
BEGIN
    WITH ActorFilmCount AS (
        SELECT actor_id, COUNT(film_id) AS total_films
        FROM film_actor
        WHERE actor_id IN (
            SELECT DISTINCT actor_id
            FROM film_actor
        )
        GROUP BY actor_id
    )
    SELECT
        a.actor_id,
        a.first_name,
        a.last_name,
        afc.total_films
    FROM actor a
    JOIN ActorFilmCount afc
        ON a.actor_id = afc.actor_id
    WHERE afc.total_films > 10;
END //

DELIMITER ;

CALL GetActorsWithMoreThanTenFilms();


/* =========================================================
   QUESTION 3
   Find customers who never made a payment.
   ========================================================= */

CREATE VIEW CustomersWithoutPayments AS
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email
FROM customer c
WHERE NOT EXISTS (
    SELECT 1
    FROM payment p
    WHERE p.customer_id = c.customer_id
);

DELIMITER //

CREATE PROCEDURE GetCustomersWithoutPayments()
BEGIN
    SELECT *
    FROM CustomersWithoutPayments;
END //

DELIMITER ;

CALL GetCustomersWithoutPayments();


/* =========================================================
   QUESTION 4
   List films whose rental rate is higher than the average.
   ========================================================= */

CREATE VIEW FilmsAboveAverageRentalRate AS
SELECT
    film_id,
    title,
    rental_rate
FROM film
WHERE rental_rate > (
    SELECT AVG(rental_rate)
    FROM film
);

DELIMITER //

CREATE PROCEDURE GetFilmsAboveAverageRentalRate()
BEGIN
    SELECT *
    FROM FilmsAboveAverageRentalRate;
END //

DELIMITER ;

CALL GetFilmsAboveAverageRentalRate();


/* =========================================================
   QUESTION 5
   List films that were never rented.
   ========================================================= */

DELIMITER //

CREATE PROCEDURE GetNeverRentedFilms()
BEGIN
    DROP TEMPORARY TABLE IF EXISTS NeverRentedFilms;

    CREATE TEMPORARY TABLE NeverRentedFilms AS
    SELECT
        f.film_id,
        f.title
    FROM film f
    WHERE NOT EXISTS (
        SELECT 1
        FROM inventory i
        JOIN rental r
            ON r.inventory_id = i.inventory_id
        WHERE i.film_id = f.film_id
    );

    SELECT *
    FROM NeverRentedFilms;

    DROP TEMPORARY TABLE IF EXISTS NeverRentedFilms;
END //

DELIMITER ;

CALL GetNeverRentedFilms();


/* =========================================================
   QUESTION 6
   Display customers who rented films in the same month
   and year as customer ID 5.
   ========================================================= */

WITH CustomerFiveRentalMonths AS (
    SELECT DISTINCT
        YEAR(rental_date) AS rental_year,
        MONTH(rental_date) AS rental_month
    FROM rental
    WHERE customer_id = 5
)
SELECT DISTINCT
    c.customer_id,
    c.first_name,
    c.last_name
FROM customer c
JOIN rental r
    ON c.customer_id = r.customer_id
JOIN CustomerFiveRentalMonths crm
    ON YEAR(r.rental_date) = crm.rental_year
    AND MONTH(r.rental_date) = crm.rental_month
WHERE c.customer_id <> 5;


/* =========================================================
   QUESTION 7
   Find staff members who handled a payment greater than
   the average payment amount.
   ========================================================= */

SELECT DISTINCT
    s.staff_id,
    s.first_name,
    s.last_name
FROM staff s
JOIN payment p
    ON s.staff_id = p.staff_id
WHERE p.amount > (
    SELECT AVG(amount)
    FROM payment
);