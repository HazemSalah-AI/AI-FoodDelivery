-- ==========================================
-- ABO HAMMAD DELIVERY SYSTEM
-- File: 04_seed_data.sql
-- Description: Sample Data
-- ==========================================

-- Cities
INSERT INTO city(city_name)
VALUES
('Abo Hammad'),
('Zagazig'),
('Belbeis'),
('Cairo');

-- Admin
INSERT INTO admin(name,email,password_hash)
VALUES
('System Admin','admin@abohammad.com','admin123');

-- Merchant
INSERT INTO merchant
(business_name,owner_name,phone,email,password_hash,status)
VALUES
('Fresh Market','Ahmed Ali','01000000001','fresh@shop.com','123456','ACTIVE');

-- Category
INSERT INTO category(merchant_id,name)
VALUES
(1,'Groceries'),
(1,'Drinks');

-- Product
INSERT INTO product
(merchant_id,category_id,name,description,price,stock_quantity,is_available)
VALUES
(1,1,'Rice','Egyptian Rice',25.50,100,true),
(1,2,'Pepsi','Soft Drink',15.00,200,true);

-- Customer
INSERT INTO customer
(first_name,last_name,phone,email,password_hash)
VALUES
('Hazem','Salah','01012345678','hazem@gmail.com','123456');

-- Driver
INSERT INTO driver
(first_name,last_name,phone,email,password_hash,vehicle_type,is_available)
VALUES
('Ali','Mahmoud','01111111111','driver@gmail.com','123456','Motorcycle',true);

-- Address
INSERT INTO address
(customer_id,title,street,city_id,latitude,longitude,is_default)
VALUES
(1,'Home','Main Street',1,30.75000000,31.50000000,true);

-- Order
INSERT INTO orders
(customer_id,merchant_id,address_id,driver_id,total_price,payment_method,order_status)
VALUES
(1,1,1,1,66.00,'Cash','Pending');

-- Order Item
INSERT INTO order_item
(order_id,product_id,quantity,unit_price,subtotal)
VALUES
(1,1,2,25.50,51.00),
(1,2,1,15.00,15.00);

-- Order Status History
INSERT INTO order_status_history
(order_id,status,changed_by)
VALUES
(1,'Pending','Customer');

-- Notification
INSERT INTO notification
(customer_id,title,message,is_read)
VALUES
(1,'Order Created','Your order has been created.',false);