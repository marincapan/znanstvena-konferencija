FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code/
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
ADD ./docker-entrypoint.sh /code/docker-entrypoint.sh
RUN chmod +x /code/docker-entrypoint.sh
ENTRYPOINT ["/code/docker-entrypoint.sh"]