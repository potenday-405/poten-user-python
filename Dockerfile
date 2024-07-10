FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install sqlalchemy
RUN pip install pymysql
RUN pip install pydantic_settings
RUN pip install python-jose
RUN pip install bcrypt

EXPOSE 9000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
