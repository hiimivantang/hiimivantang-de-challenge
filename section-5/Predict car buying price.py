# Databricks notebook source
# MAGIC %md
# MAGIC # Load training dataset
# MAGIC 
# MAGIC Load training dataset directly from `https://archive.ics.uci.edu/ml/machine-learning-databases/car/car.data` into a Pandas Dataframe. 

# COMMAND ----------

import mlflow
import os
import uuid
import shutil
from databricks.automl_runtime.sklearn.column_selector import ColumnSelector
import pandas as pd

features = ["maint", "safety", "lug_boot", "doors", "persons","class"]
col_selector = ColumnSelector(features)

df_loaded = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/car/car.data', names=['buying','maint','doors','persons','lug_boot','safety','class'], index_col =False)

# COMMAND ----------

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer


one_hot_imputers = []
 
one_hot_pipeline = Pipeline(steps=[
    ("imputers", ColumnTransformer(one_hot_imputers, remainder="passthrough")),
    ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore")),
])
 
categorical_one_hot_transformers = [("onehot", one_hot_pipeline, ["doors", "lug_boot", "maint", "persons", "safety", "class"])]

# COMMAND ----------

from sklearn.compose import ColumnTransformer

transformers = categorical_one_hot_transformers

preprocessor = ColumnTransformer(transformers, remainder="passthrough", sparse_threshold=1)

# COMMAND ----------

from sklearn.model_selection import train_test_split
import numpy as np
 
split_train_df, split_val_df, split_test_df = np.split(df_loaded.sample(frac=1, random_state=42), [int(.6*len(df_loaded)), int(.8*len(df_loaded))])
 
cols = ["doors", "lug_boot", "maint", "persons", "safety", "class"]
target_col = 'buying'
 
# Separate target column from features 
X_train = split_train_df[cols]
y_train = split_train_df[target_col]
 
X_val = split_val_df[cols]
y_val = split_val_df[target_col]
 
X_test = split_test_df[cols]
y_test = split_test_df[target_col]

# COMMAND ----------

# MAGIC %md
# MAGIC ### Train our classification model
# MAGIC 
# MAGIC - Log relevant metrics to MLflow to track runs
# MAGIC - Change the model parameters and re-run the training cell to log a different trial to the MLflow experiment
# MAGIC - To view the full list of tunable hyperparameters, check the output of the cell below

# COMMAND ----------

from sklearn.linear_model import LogisticRegression

help(LogisticRegression)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Define the objective function
# MAGIC The objective function used to find optimal hyperparameters. By default, this notebook only runs
# MAGIC this function once (`max_evals=1` in the `hyperopt.fmin` invocation) with fixed hyperparameters, but
# MAGIC hyperparameters can be tuned by modifying `space`, defined below. `hyperopt.fmin` will then use this
# MAGIC function's return value to search the space to minimize the loss.

# COMMAND ----------

import mlflow
from mlflow.models import Model, infer_signature, ModelSignature
from mlflow.pyfunc import PyFuncModel
from mlflow import pyfunc
import sklearn
from sklearn import set_config
from sklearn.pipeline import Pipeline

from hyperopt import hp, tpe, fmin, STATUS_OK, Trials

def objective(params):
  with mlflow.start_run(experiment_id="2813515716224008") as mlflow_run:
    sklr_classifier = LogisticRegression(multi_class="multinomial", **params)

    model = Pipeline([
        ("column_selector", col_selector),
        ("preprocessor", preprocessor),
        ("classifier", sklr_classifier),
    ])

    # Enable automatic logging of input samples, metrics, parameters, and models
    mlflow.sklearn.autolog(
        log_input_examples=True,
        silent=True)

    model.fit(X_train, y_train)

    
    # Log metrics for the training set
    mlflow_model = Model()
    pyfunc.add_to_model(mlflow_model, loader_module="mlflow.sklearn")
    pyfunc_model = PyFuncModel(model_meta=mlflow_model, model_impl=model)
    X_train[target_col] = y_train
    training_eval_result = mlflow.evaluate(
        model=pyfunc_model,
        data=X_train,
        targets=target_col,
        model_type="classifier",
        evaluator_config = {"log_model_explainability": False,
                            "metric_prefix": "training_"  }
    )
    sklr_training_metrics = training_eval_result.metrics
    # Log metrics for the validation set
    X_val[target_col] = y_val
    val_eval_result = mlflow.evaluate(
        model=pyfunc_model,
        data=X_val,
        targets=target_col,
        model_type="classifier",
        evaluator_config = {"log_model_explainability": False,
                            "metric_prefix": "val_"  }
    )
    sklr_val_metrics = val_eval_result.metrics
    # Log metrics for the test set
    X_test[target_col] = y_test
    test_eval_result = mlflow.evaluate(
        model=pyfunc_model,
        data=X_test,
        targets=target_col,
        model_type="classifier",
        evaluator_config = {"log_model_explainability": False,
                            "metric_prefix": "test_"  }
    )
    sklr_test_metrics = test_eval_result.metrics

    loss = sklr_val_metrics["val_f1_score"]

    # Truncate metric key names so they can be displayed together
    sklr_val_metrics = {k.replace("val_", ""): v for k, v in sklr_val_metrics.items()}
    sklr_test_metrics = {k.replace("test_", ""): v for k, v in sklr_test_metrics.items()}

    return {
      "loss": loss,
      "status": STATUS_OK,
      "val_metrics": sklr_val_metrics,
      "test_metrics": sklr_test_metrics,
      "model": model,
      "run": mlflow_run,
    }

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC The following set of parameters provides gives the best F1 validation score after performing hyperparameter tuning.
# MAGIC 
# MAGIC To perform hyperparameter tuning, modify the following parameters to widen the search. For example, when training a logistsic regression classifier, to allow the normalization to be either L1 or L2, set the value for `penalty` to `hp.choice('penalty', ['l1','l2'])`.
# MAGIC 
# MAGIC Also increase `max_evals` in the Hyperopt `fmin` function call below.

# COMMAND ----------

space = {
  "C": 0.48458618492431577,
  "penalty": "l1",
  "solver": "saga",
  "random_state": 163298345,
}

# COMMAND ----------

trials = Trials()
fmin(objective,
     space=space,
     algo=tpe.suggest,
     max_evals=1,  # Increase this when widening the hyperparameter search space.
     trials=trials)

best_result = trials.best_trial["result"]
model = best_result["model"]
mlflow_run = best_result["run"]

display(
  pd.DataFrame(
    [best_result["val_metrics"], best_result["test_metrics"]],
    index=["validation", "test"]))

set_config(display="diagram")
model

# COMMAND ----------

# MAGIC %md
# MAGIC ```
# MAGIC Maintenance = High
# MAGIC Number of doors = 4
# MAGIC Lug Boot Size = Big
# MAGIC Safety = High
# MAGIC Class Value = Good
# MAGIC ```

# COMMAND ----------

X = pd.DataFrame([['high',4,np.NaN,'big','high','good']], columns=["maint", "doors", "persons", "lug_boot", "safety", "class"])

# COMMAND ----------

model.predict(X)[0]
