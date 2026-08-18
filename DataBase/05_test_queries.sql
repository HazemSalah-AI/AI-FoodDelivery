-- ==========================================
-- ABO HAMMAD DELIVERY SYSTEM
-- File: 05_test_queries.sql
-- Description: Test Queries
-- ==========================================

-- View all customers
SELECT * FROM customer;

-- View all merchants
SELECT * FROM merchant;

-- View all drivers
SELECT * FROM driver;

-- View all products
SELECT * FROM product;

-- View all categories
SELECT * FROM category;

-- View all orders
SELECT * FROM orders;

-- Customer Orders
SELECT *
FROM orders
WHERE customer_id = 1;

-- Merchant Orders
SELECT *
FROM orders
WHERE merchant_id = 1;

-- Driver Orders
SELECT *
FROM orders
WHERE driver_id = 1;

-- Products of Merchant
SELECT *
FROM product
WHERE merchant_id = 1;

-- Products in Category
SELECT *
FROM product
WHERE category_id = 1;

-- Order Details
SELECT
o.order_id,
p.name,
oi.quantity,
oi.unit_price,
oi.subtotal
FROM orders o
JOIN order_item oi
ON o.order_id = oi.order_id
JOIN product p
ON oi.product_id = p.product_id
WHERE o.order_id = 1;

-- Customer Addresses
SELECT *
FROM address
WHERE customer_id = 1;

-- Notifications
SELECT *
FROM notification
WHERE customer_id = 1;

-- Order History
SELECT *
FROM order_status_history
WHERE order_id = 1;

-- Total Sales
SELECT SUM(total_price)
FROM orders;

-- Number of Orders
SELECT COUNT(*)
FROM orders;

-- Available Products
SELECT *
FROM product
WHERE is_available = true;

-- Available Drivers
SELECT *
FROM driver
WHERE is_available = true;