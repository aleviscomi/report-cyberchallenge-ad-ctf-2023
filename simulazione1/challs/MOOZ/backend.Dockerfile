FROM python:3.8-slim
COPY ./backend /backend
COPY ./avatars /avatars
COPY ./requirements.txt /
WORKDIR /
RUN apt-get update && apt-get install -y build-essential
RUN pip install -r /requirements.txt
CMD gunicorn -b 0.0.0.0:5000 "backend:create_app()" --access-logfile - --error-logfile - --timeout 300 -w 4