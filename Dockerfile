FROM python:3.6.5

RUN apt-get update

WORKDIR /opt/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
# RUN pip3 install -e .

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "app:app"
