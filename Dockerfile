FROM python:3.12

ADD ./app /app
RUN pip install -r /app/requirements.txt && pip install -r /app/twitter_download/requirements.txt
CMD ["python3", "/app/controller.py"]
