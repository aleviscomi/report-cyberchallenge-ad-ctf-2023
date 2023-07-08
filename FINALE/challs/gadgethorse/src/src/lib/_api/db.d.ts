import type { ColumnType } from "kysely";

export type Generated<T> = T extends ColumnType<infer S, infer I, infer U>
  ? ColumnType<S, I | undefined, U>
  : ColumnType<T, T | undefined, T>;

export interface BaseCustomProduct {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  order: Generated<number>;
}

export interface Customizations {
  id: string;
  text: string;
  font: Generated<string | null>;
  color: Generated<string | null>;
  width: string;
  height: string;
  x: string;
  y: string;
  base_product: string;
}

export interface Order {
  id: string;
  user: string;
  name: string;
  surname: string;
  address: string;
  city: string;
  country: string;
}

export interface OrderItems {
  id: Generated<number>;
  order: string;
  item: string;
  qty: number;
}

export interface Products {
  id: string;
  name: string;
  description: string;
  short_description: string;
  price: number;
  image: string;
  order: Generated<number>;
}

export interface SavedCart {
  id: Generated<number>;
  user: string;
  cart: Generated<string | null>;
}

export interface Users {
  id: string;
  name: string;
  email: string;
  password: string;
}

export interface DB {
  base_custom_product: BaseCustomProduct;
  customizations: Customizations;
  order: Order;
  order_items: OrderItems;
  products: Products;
  saved_cart: SavedCart;
  users: Users;
}
