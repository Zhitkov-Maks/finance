FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . ./finance

WORKDIR ./finance

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "finance.wsgi:application"]
