create SCHEMA acme;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA acme TO postgres;

CREATE USER keefer WITH PASSWORD 'password';
CREATE USER lucas WITH PASSWORD 'password';
CREATE USER maxi WITH PASSWORD 'password';

CREATE GROUP logistics WITH USER keefer;
CREATE GROUP analytics WITH USER lucas;
CREATE GROUP sales WITH USER maxi;


create table if not exists acme.items (
  id SERIAL primary key,
  name VARCHAR(100),
  manufacturer_name VARCHAR(100),
  cost INTEGER not null,
  weight decimal(6,2) not null
);


create table if not exists acme.customers (
  id VARCHAR(106) primary key,
  first_name VARCHAR(100) not null,
  last_name VARCHAR(100) not null,
  birth_date INTEGER not null,
  email VARCHAR(320) not null,
  mobile_no INTEGER not null
);


create table if not exists acme.sales (
  id SERIAL primary key,
  order_date timestamp not null, 
  fulfilled boolean default false
);


create table if not exists acme.sales_details (
  id SERIAL primary key,
  membership_id VARCHAR(106) references acme.customers,
  sales_id integer references acme.sales,
  item_id integer references acme.items,
  quantity integer not null
);

GRANT INSERT, UPDATE ON acme.sales, acme.sales_details TO logistics;
GRANT INSERT, UPDATE on acme.items TO sales;
GRANT SELECT ON ALL TABLES IN SCHEMA acme TO logistics, analytics, sales;
