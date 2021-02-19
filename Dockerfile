FROM python:slim

RUN pip3 install --no-cache-dir pandas

RUN pip3 install numpy

RUN pip3 install cryptography

RUN pip3 install yfinance

RUN pip3 install passlib

RUN pip3 install beautifulsoup4

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn

COPY . /usr/src/app

EXPOSE 8090

CMD [ "python3", "app.py" ]
#CMD gunicorn --workers 2 --bind 0.0.0.0:8090 app:app
