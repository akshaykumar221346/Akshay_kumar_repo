-- 1. Identify if there are duplicates in Customer table. Don't use customer id to check the duplicates
SELECT first_name, last_name, email, COUNT(*) AS duplicate_count FROM customer GROUP BY first_name, last_name, email HAVING COUNT(*) > 1;

-- 2. Number of times letter 'a' is repeated in film descriptions
SELECT title, (LENGTH(description) - LENGTH(REPLACE(LOWER(description), 'a', ''))) AS a_count FROM film;

-- 3. Number of times each vowel is repeated in film descriptions 
SELECT 
SUM(LENGTH(LOWER(description)) - LENGTH(REPLACE(LOWER(description), 'a', ''))) AS a_count,
SUM(LENGTH(LOWER(description)) - LENGTH(REPLACE(LOWER(description), 'e', ''))) AS e_count,
SUM(LENGTH(LOWER(description)) - LENGTH(REPLACE(LOWER(description), 'i', ''))) AS i_count,
SUM(LENGTH(LOWER(description)) - LENGTH(REPLACE(LOWER(description), 'o', ''))) AS o_count,
SUM(LENGTH(LOWER(description)) - LENGTH(REPLACE(LOWER(description), 'u', ''))) AS u_count
FROM film;

-- 4. Display the payments made by each customer
--  1. Month wise
SELECT c.customer_id, c.first_name, c.last_name, YEAR(p.payment_date) AS payment_year, MONTH(p.payment_date) AS payment_month, SUM(p.amount) AS total_payment FROM customer c JOIN payment p ON c.customer_id = p.customer_id GROUP BY c.customer_id, c.first_name, c.last_name, YEAR(p.payment_date), MONTH(p.payment_date);
-- 2. Year wise
SELECT c.customer_id, c.first_name, c.last_name, YEAR(p.payment_date) AS payment_year, SUM(p.amount) AS total_payment FROM customer c JOIN payment p ON c.customer_id = p.customer_id GROUP BY c.customer_id, c.first_name, c.last_name, YEAR(p.payment_date);
-- 3. Week wise
SELECT c.customer_id, c.first_name, c.last_name, YEAR(p.payment_date) AS payment_year, WEEK(p.payment_date) AS payment_week, SUM(p.amount) AS total_payment FROM customer c JOIN payment p ON c.customer_id = p.customer_id GROUP BY c.customer_id, c.first_name, c.last_name, YEAR(p.payment_date), WEEK(p.payment_date);
       

-- 5. Check if any given year is a leap year or not. You need not consider any table from sakila database. Write within the select query with hardcoded date
SELECT CASE WHEN (2024 % 400 = 0) OR (2024 % 4 = 0 AND 2024 % 100 <> 0) THEN 'Leap Year' ELSE 'Not a Leap Year' END AS Result;

-- 6. Display number of days remaining in the current year from today.
SELECT DATEDIFF(CONCAT(YEAR(CURDATE()), '-12-31'), CURDATE()) AS days_remaining;

-- 7. Display quarter number(Q1,Q2,Q3,Q4) for the payment dates from payment table.
SELECT payment_id, payment_date, CONCAT('Q', QUARTER(payment_date)) AS quarter FROM payment;