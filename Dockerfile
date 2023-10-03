FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install software-properties-common -y

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8000

# RUN sed -i 's/\r$//g' /app/start.sh
# RUN chmod +x /app/

# RUN sed -i 's/\r$//g' /app/celery/worker/start.sh
# RUN chmod +x /app/celery/worker/

# COPY ./entrypoint.sh .
# ENTRYPOINT [ "sh", "/app/entrypoint.sh" ]

