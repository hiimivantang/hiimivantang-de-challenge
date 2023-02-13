# Databricks notebook source
access_key = ""
secret_key = ""
encoded_secret_key = secret_key.replace("/", "%2F")

aws_bucket_name = "hiimivantang-canedge"
mount_name = "hiimivantang-private-bucket"

dbutils.fs.mount(f"s3a://{access_key}:{encoded_secret_key}@{aws_bucket_name}", f"/mnt/{mount_name}")
display(dbutils.fs.ls(f"/mnt/{mount_name}"))
