"""
Using Prophet, create a prediction of what the next CPU usage will be given
its history. Also calculate an error range
"""

import requests
import time
import sys
import os
import re
import pandas
from prophet import Prophet
from prometheus_client import Gauge, make_wsgi_app
from wsgiref.simple_server import make_server


class SQLInstance:
    """
    Class to hold SQL instance name and associated metrics
    """

    def __init__(self, sql_instance_name):
        self.sql_instance_name = sql_instance_name
        self.metrics = {}


class PredictionService:
    """
    Singleton class for handling SQL instance metrics predictions
    """

    # Singleton instance
    _instance = None

    # Class method to get the singleton instance
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # Constants
    DEFAULT_DAYS_BACK = "7d"
    DEFAULT_PREDICTION_PERIODS = "30"
    DEFAULT_PREDICTION_FREQUENCY = "s"
    DEFAULT_CHANGEPOINT_PRIOR_SCALE = "1.0"

    def __init__(self):
        self.prometheus_url = os.getenv("PROMETHEUS")
        self.days_back = os.getenv("DAYSBACK", self.DEFAULT_DAYS_BACK)
        self.prediction_frequency = float(
            os.getenv("PREDICTION_FREQUENCY", self.DEFAULT_PREDICTION_FREQUENCY)
        )
        self.changepoint_prior_scale = float(
            os.getenv("CHANGEPOINT_PRIOR_SCALE", self.DEFAULT_CHANGEPOINT_PRIOR_SCALE)
        )
        self.gauge_metrics = {}
        self.query_templates = {
            "cpu": "sqlserver_cpu_sqlserver_process_cpu[{days_back}]"
        }

    def get_prometheus_data(self, metric_type="cpu"):
        """
        Fetch data from Prometheus API
        """
        if not self.prometheus_url:
            raise ValueError("Prometheus URL not set in environment variables")

        # Build the query based on the metric type
        promql_query = {
            "query": self.query_templates[metric_type].format(days_back=self.days_back)
        }

        # Get the response from the prometheus API
        response = requests.get(url=self.prometheus_url, params=promql_query)
        response_json = response.json()

        # Process the response data
        dataframes = []
        for result in response_json["data"]["result"]:
            sql_instance_name = result["metric"].get("sql_instance")
            metric_name = result["metric"].get("__name__")
            dataframe = pandas.DataFrame(result["values"], columns=["ds", "y"])
            dataframes.append(
                {
                    "sql_instance": sql_instance_name,
                    "metric_name": metric_name,
                    "dataframe": dataframe,
                }
            )

        return dataframes

    def predict_metrics(self, dataframes):
        """
        Generate predictions for each SQL instance
        """
        sql_instances = []

        for data in dataframes:
            df = data["dataframe"]
            sql_instance_name = data["sql_instance"]
            metric_name = data["metric_name"]

            print(
                f"\nPredicting for: {sql_instance_name}\tMetric: {metric_name}\t"
                f"Number of metrics evaluated: {df.y.count()}"
            )

            # Prepare data for prophet
            df["ds"] = pandas.to_datetime(df["ds"], unit="s")

            # Create and fit the model
            model = Prophet(changepoint_prior_scale=self.changepoint_prior_scale)
            model.fit(df)

            # Generate future predictions
            future = model.make_future_dataframe(
                periods=self.DEFAULT_PREDICTION_PERIODS,
                freq=self.DEFAULT_PREDICTION_FREQUENCY,
            )
            forecast = model.predict(future)

            # Extract prediction values (ensuring non-negative)
            predicted_values = {
                f"{metric_name}_yhat": max(0, forecast[["yhat"]].tail(1).values[0][0]),
                f"{metric_name}_yhat_lower": max(
                    0, forecast[["yhat_lower"]].tail(1).values[0][0]
                ),
                f"{metric_name}_yhat_upper": max(
                    0, forecast[["yhat_upper"]].tail(1).values[0][0]
                ),
            }

            # Create instance and add to list
            instance = SQLInstance(sql_instance_name)
            instance.metrics = predicted_values
            sql_instances.append(instance)

        # Print all predictions
        self._print_predictions(sql_instances)

        return sql_instances

    def _print_predictions(self, sql_instances):
        """
        Print prediction results
        """
        for instance in sql_instances:
            print(f"\nSQL Instance: {instance.sql_instance_name}")
            for metric_name, metric_value in instance.metrics.items():
                print(f"\tMetric: {metric_name}\tValue: {str(metric_value)}")

    def get_predictions(self):
        """
        Retrieve and process data to generate predictions
        """
        dataframes = self.get_prometheus_data()
        return self.predict_metrics(dataframes)

    def update_metrics(self):
        """
        Update Prometheus gauge metrics with predictions
        """
        predicted_metrics = self.get_predictions()

        # Initialize gauge metrics if not already done
        if not self.gauge_metrics and predicted_metrics:
            print("Creating more metrics")
            self._initialize_gauge_metrics(predicted_metrics[0])

        # Update all gauges with new values
        for instance in predicted_metrics:
            for metric_name, metric_value in instance.metrics.items():
                if metric_name in self.gauge_metrics:
                    self.gauge_metrics[metric_name].labels(
                        sql_instance=instance.sql_instance_name
                    ).set(metric_value)

        return predicted_metrics

    def _initialize_gauge_metrics(self, sample_instance):
        """
        Initialize gauge metrics based on a sample instance
        """

        for metric_name in sample_instance.metrics.keys():
            self.gauge_metrics[metric_name] = Gauge(
                metric_name, f"Predicted Metric: {metric_name}", ["sql_instance"]
            )


# TODO: This currently doesnt work because it tries to create a gauge every time
# it launches. See how the original script does it and fix it
