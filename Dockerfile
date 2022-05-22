FROM python:3.9.13-slim

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .


ENTRYPOINT [ "sh" ]

CMD [ "-c", "uvicorn server:app --port 8000 --host 0.0.0.0" ]
