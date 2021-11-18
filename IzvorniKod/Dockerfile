FROM python:3.8
ENV PYTHONUNBUFFERED 1
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]