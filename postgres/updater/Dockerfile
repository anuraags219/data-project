FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY postgres/updater/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY postgres/updater/update_customers.py .

CMD ["python", "update_customers.py"]