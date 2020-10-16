FROM python:3.6
ENV PYTHONUNBUFFERED=1
RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  && apt-get install -y python3-dev \ 
  && apt-get install -y default-libmysqlclient-dev
  
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/