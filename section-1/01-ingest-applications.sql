-- Databricks notebook source
CREATE OR REFRESH STREAMING LIVE TABLE bronze_applications
AS SELECT * FROM cloud_files("/mnt/hiimivantang-private-bucket/membership_applications", "csv", map("cloudFiles.inferColumnTypes", "true", "header", "true"))

-- COMMAND ----------

CREATE OR REFRESH LIVE TABLE silver_applications_prepared
AS SELECT name, 
split(name, ' ')[0] as first_name,
split(name, ' ')[1] as last_name, 
email,
CASE WHEN date_of_birth regexp '^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$' THEN to_date(date_of_birth, 'yyyy-MM-dd')
WHEN date_of_birth regexp '^[0-9]{2}\-[0-9]{2}\-[0-9]{4}$' THEN to_date(date_of_birth, 'dd-MM-yyyy') 
WHEN date_of_birth regexp '^[0-9]{2}\/[0-9]{2}\/[0-9]{4}$' THEN to_date(date_of_birth, 'MM/dd/yyyy')
WHEN date_of_birth regexp '^[0-9]{4}\/[0-9]{2}\/[0-9]{2}$' THEN to_date(date_of_birth, 'yyyy/MM/dd') ELSE NULL END as parsed_date_of_birth,
mobile_no
from live.bronze_applications;

-- COMMAND ----------

CREATE OR REFRESH LIVE TABLE silver_applications_prepared_enriched
SELECT 
concat(last_name, '_', substring(sha2(date_format( parsed_date_of_birth, 'yyyyMMdd'), '256'), 0, 5)) as membership_id,
name,
first_name,
last_name,
date_format(parsed_date_of_birth, 'yyyyMMdd') as date_of_birth,
parsed_date_of_birth <= (DATE'2022-01-1' - INTERVAL '18' YEAR) as above_18,
email regexp '^.*@.*(.com|.net)' as valid_email,
mobile_no regexp '^[0-9]{8}$' as valid_mobile
from live.silver_applications_prepared

-- COMMAND ----------

CREATE
OR REFRESH LIVE TABLE gold_successful_applications(
  CONSTRAINT name_not_null EXPECT (name IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_age EXPECT (above_18 IS TRUE) ON VIOLATION DROP ROW,
  CONSTRAINT valid_email EXPECT (valid_email IS TRUE) ON VIOLATION DROP ROW,
  CONSTRAINT valid_mobile EXPECT (valid_mobile IS TRUE) ON VIOLATION DROP ROW
) AS
SELECT
  *
FROM
  live.silver_applications_prepared_enriched

-- COMMAND ----------

CREATE
OR REFRESH LIVE TABLE gold_unsuccessful_applications AS
SELECT
  *
FROM
  live.silver_applications_prepared_enriched
WHERE
  name IS NULL
  OR NOT above_18
  OR NOT valid_email
  OR NOT valid_mobile
