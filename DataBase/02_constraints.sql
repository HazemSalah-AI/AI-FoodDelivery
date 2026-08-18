-- ==========================================
-- ABO HAMMAD DELIVERY SYSTEM
-- File: 02_constraints.sql
-- Description: Add Constraints
-- ==========================================

--------------------
-- CITY
--------------------
ALTER TABLE city
ADD CONSTRAINT pk_city PRIMARY KEY (city_id);

ALTER TABLE city
ADD CONSTRAINT uq_city_name UNIQUE (city_name);

--------------------
-- ADMIN
--------------------
ALTER TABLE admin
ADD CONSTRAINT pk_admin PRIMARY KEY (admin_id);

ALTER TABLE admin
ADD CONSTRAINT uq_admin_email UNIQUE (email);

--------------------
-- CUSTOMER
--------------------
ALTER TABLE customer
ADD CONSTRAINT pk_customer PRIMARY KEY (customer_id);

ALTER TABLE customer
ADD CONSTRAINT uq_customer_email UNIQUE (email);

ALTER TABLE customer
ADD CONSTRAINT uq_customer_phone UNIQUE (phone);

--------------------
-- MERCHANT
--------------------
ALTER TABLE merchant
ADD CONSTRAINT pk_merchant PRIMARY KEY (merchant_id);

ALTER TABLE merchant
ADD CONSTRAINT uq_merchant_email UNIQUE (email);

ALTER TABLE merchant
ADD CONSTRAINT uq_merchant_phone UNIQUE (phone);

--------------------
-- DRIVER
--------------------
ALTER TABLE driver
ADD CONSTRAINT pk_driver PRIMARY KEY (driver_id);

ALTER TABLE driver
ADD CONSTRAINT uq_driver_email UNIQUE (email);

ALTER TABLE driver
ADD CONSTRAINT uq_driver_phone UNIQUE (phone);

--------------------
-- CATEGORY
--------------------
ALTER TABLE category
ADD CONSTRAINT pk_category PRIMARY KEY (category_id);

ALTER TABLE category
ADD CONSTRAINT fk_category_merchant
FOREIGN KEY (merchant_id)
REFERENCES merchant(merchant_id);

--------------------
-- ADDRESS
--------------------
ALTER TABLE address
ADD CONSTRAINT pk_address PRIMARY KEY (address_id);

ALTER TABLE address
ADD CONSTRAINT fk_address_customer
FOREIGN KEY (customer_id)
REFERENCES customer(customer_id);

ALTER TABLE address
ADD CONSTRAINT fk_address_city
FOREIGN KEY (city_id)
REFERENCES city(city_id);

--------------------
-- PRODUCT
--------------------
ALTER TABLE product
ADD CONSTRAINT pk_product PRIMARY KEY (product_id);

ALTER TABLE product
ADD CONSTRAINT fk_product_merchant
FOREIGN KEY (merchant_id)
REFERENCES merchant(merchant_id);

ALTER TABLE product
ADD CONSTRAINT fk_product_category
FOREIGN KEY (category_id)
REFERENCES category(category_id);

--------------------
-- ORDERS
--------------------
ALTER TABLE orders
ADD CONSTRAINT pk_orders PRIMARY KEY (order_id);

ALTER TABLE orders
ADD CONSTRAINT fk_orders_customer
FOREIGN KEY (customer_id)
REFERENCES customer(customer_id);

ALTER TABLE orders
ADD CONSTRAINT fk_orders_merchant
FOREIGN KEY (merchant_id)
REFERENCES merchant(merchant_id);

ALTER TABLE orders
ADD CONSTRAINT fk_orders_address
FOREIGN KEY (address_id)
REFERENCES address(address_id);

ALTER TABLE orders
ADD CONSTRAINT fk_orders_driver
FOREIGN KEY (driver_id)
REFERENCES driver(driver_id);

--------------------
-- ORDER_ITEM
--------------------
ALTER TABLE order_item
ADD CONSTRAINT pk_order_item PRIMARY KEY (order_item_id);

ALTER TABLE order_item
ADD CONSTRAINT fk_order_item_order
FOREIGN KEY (order_id)
REFERENCES orders(order_id);

ALTER TABLE order_item
ADD CONSTRAINT fk_order_item_product
FOREIGN KEY (product_id)
REFERENCES product(product_id);

--------------------
-- ORDER_STATUS_HISTORY
--------------------
ALTER TABLE order_status_history
ADD CONSTRAINT pk_order_status_history PRIMARY KEY (history_id);

ALTER TABLE order_status_history
ADD CONSTRAINT fk_order_status_history_order
FOREIGN KEY (order_id)
REFERENCES orders(order_id);

--------------------
-- NOTIFICATION
--------------------
ALTER TABLE notification
ADD CONSTRAINT pk_notification PRIMARY KEY (notification_id);

ALTER TABLE notification
ADD CONSTRAINT fk_notification_customer
FOREIGN KEY (customer_id)
REFERENCES customer(customer_id);

ALTER TABLE notification
ADD CONSTRAINT fk_notification_merchant
FOREIGN KEY (merchant_id)
REFERENCES merchant(merchant_id);

ALTER TABLE notification
ADD CONSTRAINT fk_notification_driver
FOREIGN KEY (driver_id)
REFERENCES driver(driver_id);