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


class Container:
    """
    Class to hold container information and metrics
    """

    def __init__(self, name):
        self.name = name
        self.metrics = {}


class PredictionService:
    """
    Singleton class for handling container metrics predictions
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
        if not self.prometheus_url:
            raise ValueError("PROMETHEUS URL not provided")
        self.days_back = os.getenv("DAYSBACK", self.DEFAULT_DAYS_BACK)
        self.prediction_periods = int(
            os.getenv("PREDICTION_PERIODS", self.DEFAULT_PREDICTION_PERIODS)
        )
        self.prediction_frequency = os.getenv(
            "PREDICTION_FREQUENCY", self.DEFAULT_PREDICTION_FREQUENCY
        )
        self.changepoint_prior_scale = float(
            os.getenv("CHANGEPOINT_PRIOR_SCALE", self.DEFAULT_CHANGEPOINT_PRIOR_SCALE)
        )
        self.gauge_metrics = {}
        self.metric_label = os.getenv("METRIC_LABEL")
        if not self.metric_label:
            raise ValueError("METRIC_LABEL envvar not provided")
        self.metric_name = os.getenv("METRIC_NAME")
        if not self.metric_name:
            raise ValueError("METRIC_NAME envvar not provided")
        self.metric_type = os.getenv("METRIC_TYPE")
        if not self.metric_name:
            raise ValueError("METRIC_NAME envvar not provided")
        self.query_templates = {self.metric_name: self.metric_type + "[{days_back}]"}

        print("Initialised Prediction Service")
        print(f"Prometheus URL: {self.prometheus_url}")
        print(f"Days Back: {self.days_back}")
        print(f"Prediction Periods: {self.prediction_periods}")
        print(f"Prediction Frequency: {self.prediction_frequency}")
        print(f"Changepoint Prior Scale: {self.changepoint_prior_scale}")
        print(f"Metric Label: {self.metric_label}")
        print(f"Metric Name: {self.metric_name}")
        print(f"Metric Type: {self.metric_type}")

    def get_prometheus_data(self, metric_type="cpu"):
        """
        Fetch data from Prometheus API
        """
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
            container_name = result["metric"].get(self.metric_label)
            metric_name = result["metric"].get("__name__")
            dataframe = pandas.DataFrame(result["values"], columns=["ds", "y"])
            dataframes.append(
                {
                    "container_name": container_name,
                    "metric_name": metric_name,
                    "dataframe": dataframe,
                }
            )

        return dataframes

    def _clamp_value(self, value):
        """
        Ensure that the value is clamped to 0 <= x <= 1
        """
        return max(0, value.tail(1).values[0][0])

    def _extract_prediction_values(self, forecast):
        """
        Extract prediction values and ensure they are non-negative by clamping them.
        """
        predicted_values = {
            f"{self.metric_type}_yhat": self._clamp_value(forecast[["yhat"]]),
            f"{self.metric_type}_yhat_lower": self._clamp_value(forecast[["yhat_lower"]]),
            f"{self.metric_type}_yhat_upper": self._clamp_value(forecast[["yhat_upper"]]),
        }
        return predicted_values

    def predict_metrics(self, dataframes):
        """
        Generate predictions for each container
        """
        containers = []

        for data in dataframes:
            df = data["dataframe"]
            container_name = data["container_name"]
            metric_name = data["metric_name"]

            print(
                f"\nPredicting for: {container_name}\tMetric: {metric_name}\t"
                f"Number of metrics evaluated: {df.y.count()}"
            )

            # Prepare data for prophet
            df["ds"] = pandas.to_datetime(df["ds"], unit="s")

            # Create and fit the model
            model = Prophet(changepoint_prior_scale=self.changepoint_prior_scale)
            model.fit(df)

            # Generate future predictions
            future = model.make_future_dataframe(
                periods=self.prediction_periods,
                freq=self.prediction_frequency,
            )
            forecast = model.predict(future)

            predicted_values = self._extract_prediction_values(forecast)

            # Create container and add to list
            container = Container(container_name)
            container.metrics = predicted_values
            containers.append(container)

        # Print all predictions
        self._print_predictions(containers)

        return containers

    def _print_predictions(self, containers):
        """
        Print prediction results
        """
        for container in containers:
            print(f"\nContainer: {container.name}")
            for metric_name, metric_value in container.metrics.items():
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
        for container in predicted_metrics:
            for metric_name, metric_value in container.metrics.items():
                if metric_name in self.gauge_metrics:
                    self.gauge_metrics[metric_name].labels(
                        container_name=container.name
                    ).set(metric_value)

        return predicted_metrics

    def _initialize_gauge_metrics(self, sample_container):
        """
        Initialize gauge metrics based on a sample container
        """

        for metric_name in sample_container.metrics.keys():
            self.gauge_metrics[metric_name] = Gauge(
                metric_name, f"Predicted Metric: {metric_name}", ["container_name"]
            )
