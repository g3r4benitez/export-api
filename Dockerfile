FROM python:3.9

EXPOSE 8000

WORKDIR /code

# Install requirements.txt
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app app

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
