
FROM python:3.11

# Ustaw katalog roboczy na /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN apt-get update && apt-get install -y netcat-openbsd


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]