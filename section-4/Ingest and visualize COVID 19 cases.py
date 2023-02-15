# Databricks notebook source
dbutils.widgets.dropdown("timeframe", "1 year" ,["All-time", "2 weeks", "30 days", "3 months", "6 months", "1 year"])

# COMMAND ----------

df = spark.read.option("multiline","true").json("/FileStore/tables/covid")

# COMMAND ----------

df.createOrReplaceTempView('covid_cases')

# COMMAND ----------

# MAGIC %sql select * from covid_cases;

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC select CASE WHEN "${timeframe}"=="1 year" then current_date - INTERVAL '1' YEAR 
# MAGIC WHEN "${timeframe}"=="6 months" then current_date - INTERVAL '6' MONTH 
# MAGIC WHEN "${timeframe}"=="3 months" then current_date - INTERVAL '3' MONTH
# MAGIC WHEN "${timeframe}"=="30 days" then current_date - INTERVAL '30' DAY
# MAGIC WHEN "${timeframe}"=="2 weeks" then current_date - INTERVAL '14' DAY
# MAGIC WHEN "${timeframe}"=="All-time" then current_date - INTERVAL '5' YEAR 
# MAGIC ELSE NULL END as from_date

# COMMAND ----------

# MAGIC %sql 
# MAGIC 
# MAGIC select date_format(Date, 'dd-MM-yyy') as Date, 'Confirmed' as status, Confirmed - LAG(Confirmed, 1) OVER (ORDER BY Date) as count from covid_cases where Confirmed>0 and Date > (select CASE WHEN "${timeframe}"=="1 year" then current_date - INTERVAL '1' YEAR 
# MAGIC WHEN "${timeframe}"=="6 months" then current_date - INTERVAL '6' MONTH 
# MAGIC WHEN "${timeframe}"=="3 months" then current_date - INTERVAL '3' MONTH
# MAGIC WHEN "${timeframe}"=="30 days" then current_date - INTERVAL '30' DAY
# MAGIC WHEN "${timeframe}"=="2 weeks" then current_date - INTERVAL '14' DAY
# MAGIC WHEN "${timeframe}"=="All-time" then current_date - INTERVAL '5' YEAR 
# MAGIC ELSE NULL END as from_date)
# MAGIC UNION
# MAGIC select date_format(Date, 'dd-MM-yyy') as Date, 'Deaths' as status, Deaths - LAG(Deaths, 1) OVER (ORDER BY Date) as count from covid_cases where Confirmed>0 and Date > (select CASE WHEN "${timeframe}"=="1 year" then current_date - INTERVAL '1' YEAR 
# MAGIC WHEN "${timeframe}"=="6 months" then current_date - INTERVAL '6' MONTH 
# MAGIC WHEN "${timeframe}"=="3 months" then current_date - INTERVAL '3' MONTH
# MAGIC WHEN "${timeframe}"=="30 days" then current_date - INTERVAL '30' DAY
# MAGIC WHEN "${timeframe}"=="2 weeks" then current_date - INTERVAL '14' DAY
# MAGIC WHEN "${timeframe}"=="All-time" then current_date - INTERVAL '5' YEAR 
# MAGIC ELSE NULL END as from_date)

# COMMAND ----------


