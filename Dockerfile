FROM python:3.11.1-alpine3.17
WORKDIR /auth
COPY . /auth
RUN pip3 install -r requirements.txt
EXPOSE 8020
CMD python3 ./app.py