FROM frolvlad/alpine-python3

WORKDIR /app


WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app


ENV PORT 5000
EXPOSE 5000/tcp

CMD ["python", "application.py" ]
