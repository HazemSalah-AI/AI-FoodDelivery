export type Role = "Customer" | "Merchant" | "Driver" | "Admin";
export type User = {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: Role;
  is_active: boolean;
};
export type Page<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};
export type Merchant = {
  id: number;
  business_name: string;
  description: string;
  status: string;
  is_open: boolean;
};
export type Product = {
  id: number;
  merchant_id: number;
  category_id: number | null;
  name: string;
  description: string;
  price: string;
  stock_quantity: number;
  is_available: boolean;
};
export type Category = { id: number; merchant_id: number; name: string };
export type Named = { id: number; name: string; city_id?: number };
export type Address = {
  id: number;
  title: string;
  street: string;
  city_id: number;
  area_id: number | null;
  latitude: string;
  longitude: string;
  is_default: boolean;
};
export type Cart = {
  merchant_id: number | null;
  items: {
    product_id: number;
    name: string;
    price: string;
    quantity: number;
    stock_quantity: number;
    is_available: boolean;
  }[];
  subtotal: string;
  delivery_fee: string;
};
export type Assignment = {
  id: number;
  order_id: number;
  driver_id: number;
  status: string;
  reason: string | null;
  created_at: string;
};
export type Order = {
  id: number;
  customer_id: number;
  merchant_id: number;
  customer_name: string;
  customer_phone: string;
  merchant_name: string;
  status: string;
  payment_method: string;
  total_price: string;
  delivery_fee: string;
  address_snapshot: {
    title: string;
    street: string;
    city_id: number;
    latitude: string;
    longitude: string;
  };
  rejection_reason: string | null;
  created_at: string;
  items: {
    product_id: number;
    product_name: string;
    quantity: number;
    unit_price: string;
  }[];
  history: { status: string; note: string; created_at: string }[];
  assignment: Assignment | null;
};
export type Notice = {
  id: number;
  order_id: number | null;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
};
export type Driver = {
  id: number;
  name: string;
  phone: string;
  is_active: boolean;
  is_available: boolean;
  last_seen: string | null;
  busy: boolean;
  latitude: string | null;
  longitude: string | null;
  location_updated_at: string | null;
};
export type Stats = {
  orders_total: number;
  pending: number;
  ready: number;
  on_delivery: number;
  delivered: number;
  cod_total: string;
};
export type Availability = {
  is_available: boolean;
  last_seen: string | null;
  busy: boolean;
};
