from google.cloud import monitoring_v3
from datetime import datetime
from zoneinfo import ZoneInfo

client = monitoring_v3.MetricServiceClient()
PROJECT_ID = "scorify-480307"
PROJECT_NAME = f"projects/{PROJECT_ID}"

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")

def push_leads_processed(count: int):
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/leads_processed"
    series.resource.type = "global"
    point = series.points.add()
    point.value.double_value = count
    point.interval.end_time.seconds = int(datetime.now(JAKARTA_TZ).timestamp())
    client.create_time_series(name=PROJECT_NAME, time_series=[series])

def push_leads_skipped(count: int):
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/leads_skipped"
    series.resource.type = "global"
    point = series.points.add()
    point.value.double_value = count
    point.interval.end_time.seconds = int(datetime.now(JAKARTA_TZ).timestamp())
    client.create_time_series(name=PROJECT_NAME, time_series=[series])

def push_batch_duration(seconds: float):
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/batch_duration_seconds"
    series.resource.type = "global"
    point = series.points.add()
    point.value.double_value = seconds
    point.interval.end_time.seconds = int(datetime.now(JAKARTA_TZ).timestamp())
    client.create_time_series(name=PROJECT_NAME, time_series=[series])

def push_batch_errors(count: int):
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/batch_errors"
    series.resource.type = "global"
    point = series.points.add()
    point.value.double_value = count
    point.interval.end_time.seconds = int(datetime.now(JAKARTA_TZ).timestamp())
    client.create_time_series(name=PROJECT_NAME, time_series=[series])
