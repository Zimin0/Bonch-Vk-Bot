FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ADD . /app

WORKDIR /app

RUN pip install -r requirements/dev.txt
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
