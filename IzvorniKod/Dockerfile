FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod a+x /docker-entrypoint.sh
<<<<<<< HEAD
ENTRYPOINT ["bash","/docker-entrypoint.sh"]

=======
ENTRYPOINT ["bash","/docker-entrypoint.sh"]
>>>>>>> 970e712beb6a2224db491dcbda6b45258e18d8b1
