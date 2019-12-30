FROM python:3.6-alpine

RUN adduser -D itora

WORKDIR /home/itora

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/prod.txt

COPY app app
COPY migrations migrations
COPY itora.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP itora.py

RUN chown -R itora:itora ./
USER itora

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
