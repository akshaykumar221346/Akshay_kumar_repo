USE sakila;

-- =========================================================
-- QUESTION 1
-- Customers who have made more than 5 payments
-- Technique: SUBQUERY
-- =========================================================

SELECT customer_id, first_name, last_name
FROM customer
WHERE customer_id IN (
    SELECT customer_id
    FROM payment
    GROUP BY customer_id
    HAVING COUNT(*) > 5
);


-- =========================================================
-- QUESTION 2
-- Actors who acted in more than 10 films
-- Technique: SUBQUERY
-- =========================================================

SELECT actor_id, first_name, last_name
FROM actor
WHERE actor_id IN (
    SELECT actor_id
    FROM film_actor
    GROUP BY actor_id
    HAVING COUNT(film_id) > 10
);


-- =========================================================
-- QUESTION 3
-- Customers who never made a payment
-- Technique: SUBQUERY
-- =========================================================

SELECT customer_id, first_name, last_name
FROM customer
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM payment
);


-- =========================================================
-- QUESTION 4
-- Films whose rental rate is greater than the average rental rate
-- Technique: SUBQUERY
-- =========================================================

SELECT film_id, title, rental_rate
FROM film
WHERE rental_rate > (
    SELECT AVG(rental_rate)
    FROM film
);


-- =========================================================
-- QUESTION 5
-- Films that were never rented
-- Technique: SUBQUERY
-- =========================================================

SELECT film_id, title
FROM film
WHERE film_id NOT IN (
    SELECT DISTINCT i.film_id
    FROM inventory i
    JOIN rental r
        ON i.inventory_id = r.inventory_id
);


-- =========================================================
-- QUESTION 6
-- Customers who rented movies in the same month
-- as customer ID 5
-- Technique: CTE
-- =========================================================

WITH customer5_months AS (
    SELECT DISTINCT MONTH(rental_date) AS rental_month
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
WHERE MONTH(r.rental_date) IN (
    SELECT rental_month
    FROM customer5_months
)
AND c.customer_id <> 5;


-- =========================================================
-- QUESTION 7
-- Staff members whose total handled payment amount
-- is greater than the average staff payment total
-- Technique: CTE
-- =========================================================

WITH staff_totals AS (
    SELECT
        staff_id,
        SUM(amount) AS total_amount
    FROM payment
    GROUP BY staff_id
)

SELECT
    staff_id,
    total_amount
FROM staff_totals
WHERE total_amount > (
    SELECT AVG(total_amount)
    FROM staff_totals
);


-- =========================================================
-- QUESTION 8
-- Films whose rental duration is above the average
-- Technique: VIEW
-- =========================================================

CREATE OR REPLACE VIEW above_average_rental_duration AS
SELECT
    film_id,
    title,
    rental_duration
FROM film
WHERE rental_duration > (
    SELECT AVG(rental_duration)
    FROM film
);

SELECT *
FROM above_average_rental_duration;


-- =========================================================
-- QUESTION 9
-- Customers who have the same address as customer ID 1
-- Technique: VIEW
-- =========================================================

CREATE OR REPLACE VIEW same_address_as_customer1 AS
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.address_id
FROM customer c
WHERE c.address_id = (
    SELECT address_id
    FROM customer
    WHERE customer_id = 1
)
AND c.customer_id <> 1;

SELECT *
FROM same_address_as_customer1;


-- =========================================================
-- QUESTION 10
-- Payments greater than the average payment amount
-- Technique: TEMPORARY TABLE
-- =========================================================

CREATE TEMPORARY TABLE high_payments AS
SELECT
    payment_id,
    customer_id,
    staff_id,
    amount,
    payment_date
FROM payment
WHERE amount > (
    SELECT AVG(amount)
    FROM payment
);

SELECT *
FROM high_payments;