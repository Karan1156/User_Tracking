# core/health_scheduler.py
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO)

def check_health():
    try:
        response = requests.get("http://127.0.0.1:8000/health/")
        if response.status_code == 200:
            logging.info("Server is healthy")
        else:
            logging.warning(f"Health check failed with status {response.status_code}")
    except Exception as e:
        logging.error(f"Health check exception: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(check_health, 'interval', minutes=5)
scheduler.start()
