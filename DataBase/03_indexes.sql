-- ==========================================
-- ABO HAMMAD DELIVERY SYSTEM
-- File: 03_indexes.sql
-- Description: Create Indexes
-- ==========================================

-- CUSTOMER
CREATE INDEX idx_customer_email ON customer(email);
CREATE INDEX idx_customer_phone ON customer(phone);

-- MERCHANT
CREATE INDEX idx_merchant_email ON merchant(email);
CREATE INDEX idx_merchant_phone ON merchant(phone);

-- DRIVER
CREATE INDEX idx_driver_email ON driver(email);
CREATE INDEX idx_driver_phone ON driver(phone);
CREATE INDEX idx_driver_available ON driver(is_available);

-- PRODUCT
CREATE INDEX idx_product_name ON product(name);
CREATE INDEX idx_product_merchant ON product(merchant_id);
CREATE INDEX idx_product_category ON product(category_id);

-- CATEGORY
CREATE INDEX idx_category_merchant ON category(merchant_id);

-- ADDRESS
CREATE INDEX idx_address_customer ON address(customer_id);
CREATE INDEX idx_address_city ON address(city_id);

-- ORDERS
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_merchant ON orders(merchant_id);
CREATE INDEX idx_orders_driver ON orders(driver_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ORDER ITEM
CREATE INDEX idx_order_item_order ON order_item(order_id);
CREATE INDEX idx_order_item_product ON order_item(product_id);

-- ORDER STATUS HISTORY
CREATE INDEX idx_history_order ON order_status_history(order_id);

-- NOTIFICATION
CREATE INDEX idx_notification_customer ON notification(customer_id);
CREATE INDEX idx_notification_driver ON notification(driver_id);
CREATE INDEX idx_notification_merchant ON notification(merchant_id);