from google.cloud import monitoring_v3
from datetime import datetime
from zoneinfo import ZoneInfo
from google.protobuf.timestamp_pb2 import Timestamp 
import os
from dotenv import load_dotenv


try:
    client = monitoring_v3.MetricServiceClient()
except Exception as e:
    print("[Monitoring Disabled] No Google credentials found:", e)
    client = None
load_dotenv() 

PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_NAME = f"projects/{PROJECT_ID}"
JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


def _create_point(value, value_key="double_value"):
    now = datetime.now(JAKARTA_TZ)
    timestamp = Timestamp()
    timestamp.seconds = int(now.timestamp())
    
   
    return monitoring_v3.Point({
        "interval": {"end_time": timestamp},
        "value": {value_key: value},
    })

def push_leads_processed(count: int):
    if not client:
        return
        
    point = _create_point(count)
    
    series = monitoring_v3.TimeSeries({
        "metric": {"type": "custom.googleapis.com/leads_processed"},
        "resource": {"type": "global"},
        "points": [point], 
    })
    client.create_time_series(name=PROJECT_NAME, time_series=[series])

def push_leads_skipped(count: int):
    if not client:
        return
        
    point = _create_point(count)
    
    series = monitoring_v3.TimeSeries({
        "metric": {"type": "custom.googleapis.com/leads_skipped"},
        "resource": {"type": "global"},
        "points": [point],
    })
    client.create_time_series(name=PROJECT_NAME, time_series=[series])

def push_batch_duration(seconds: float):
    if not client:
        return
        
    point = _create_point(seconds) 
    
    series = monitoring_v3.TimeSeries({
        "metric": {"type": "custom.googleapis.com/batch_duration_seconds"},
        "resource": {"type": "global"},
        "points": [point],
    })
    client.create_time_series(name=PROJECT_NAME, time_series=[series])

def push_batch_errors(count: int):
    if not client:
        return
        
    point = _create_point(count)
    
    series = monitoring_v3.TimeSeries({
        "metric": {"type": "custom.googleapis.com/batch_errors"},
        "resource": {"type": "global"},
        "points": [point],
    })
    client.create_time_series(name=PROJECT_NAME, time_series=[series])