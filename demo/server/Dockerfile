FROM python:3.8-slim-buster
EXPOSE 80
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
COPY server.py /app
RUN python -m pip install -r requirements.txt
CMD ["python", "server.py"]