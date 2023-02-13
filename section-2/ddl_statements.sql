create table if not exists items (
  id SERIAL primary key,
  name VARCHAR(100),
  manufacturer_name VARCHAR(100),
  cost INTEGER not null,
  weight decimal(6,2) not null
);



create table if not exists customers (
  id VARCHAR(106) primary key,
  first_name VARCHAR(100) not null,
  last_name VARCHAR(100) not null,
  birth_date INTEGER not null,
  email VARCHAR(320) not null,
  mobile_no INTEGER not null
);



create table if not exists sales (
  id SERIAL primary key,
  order_date timestamp not null, 
  fulfilled boolean default false
);



create table if not exists sales_details (
  id SERIAL primary key,
  membership_id VARCHAR(106) references customers,
  sales_id integer references sales,
  item_id integer references items,
  quantity integer not null
);
