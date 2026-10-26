FROM python:3.12-slim

ADD ./app /app
RUN pip install--no-cache-dir -r /app/requirements.txt -r /app/twitter_download/requirements.txt
CMD ["python3", "/app/controller.py"]
