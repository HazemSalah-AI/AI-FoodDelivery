-- ==========================================
-- ABO HAMMAD DELIVERY SYSTEM
-- File: 01_create_tables.sql
-- Description: Create all database tables
-- ==========================================

CREATE TABLE city (
    city_id BIGINT GENERATED ALWAYS AS IDENTITY,
    city_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE admin (
    admin_id BIGINT GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP
);

CREATE TABLE customer (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE merchant (
    merchant_id BIGINT GENERATED ALWAYS AS IDENTITY,
    business_name VARCHAR(150) NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE driver (
    driver_id BIGINT GENERATED ALWAYS AS IDENTITY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    vehicle_type VARCHAR(50),
    is_available BOOLEAN,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE category (
    category_id BIGINT GENERATED ALWAYS AS IDENTITY,
    merchant_id BIGINT,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE address (
    address_id BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id BIGINT,
    title VARCHAR(100),
    street VARCHAR(255),
    city_id BIGINT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_default BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE product (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY,
    merchant_id BIGINT,
    category_id BIGINT,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    stock_quantity INT,
    image_url VARCHAR(255),
    is_available BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id BIGINT,
    merchant_id BIGINT,
    address_id BIGINT,
    driver_id BIGINT,
    total_price DECIMAL(10,2),
    payment_method VARCHAR(20),
    order_status VARCHAR(30),
    rejection_reason VARCHAR(255),
    created_at TIMESTAMP,
    accepted_at TIMESTAMP,
    assigned_at TIMESTAMP,
    picked_up_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP
);

CREATE TABLE order_item (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY,
    order_id BIGINT,
    product_id BIGINT,
    quantity INT,
    unit_price DECIMAL(10,2),
    subtotal DECIMAL(10,2)
);

CREATE TABLE order_status_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY,
    order_id BIGINT,
    status VARCHAR(30),
    changed_by VARCHAR(20),
    note VARCHAR(255),
    created_at TIMESTAMP
);

CREATE TABLE notification (
    notification_id BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id BIGINT,
    merchant_id BIGINT,
    driver_id BIGINT,
    title VARCHAR(150),
    message TEXT,
    is_read BOOLEAN,
    created_at TIMESTAMP
);