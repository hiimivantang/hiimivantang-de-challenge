# Databricks notebook source
successful_applications = df = table('gold_successful_applications')
successful_applications.write.format('csv').mode('overwrite').option('header',True).save("/mnt/hiimivantang-private-bucket/csv/successful_applications/successful_applications.csv")

# COMMAND ----------

failed_applications = df = table('gold_unsuccessful_applications')
failed_applications.write.format('csv').mode('overwrite').option('header',True).save("/mnt/hiimivantang-private-bucket/csv/failed_applications/failed_applications.csv")

# COMMAND ----------

# MAGIC %sh 
# MAGIC rm -rf /dbfs/mnt/hiimivantang-canedge

# COMMAND ----------


