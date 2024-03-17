FROM python:3.11

WORKDIR /app

COPY transport_bot.py /app
COPY requirements.txt /app
COPY /src /app/src
COPY /secrets /app/secrets

RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

CMD [ "python", "-u", "transport_bot.py" ]