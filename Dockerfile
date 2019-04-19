FROM frolvlad/alpine-python3

WORKDIR /app


WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app


ENV PORT 33445
EXPOSE 33445/tcp

CMD ["python", "application.py" ]
