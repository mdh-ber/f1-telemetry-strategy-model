FROM python:3.12-slim

WORKDIR /app

# Existing project dependencies
COPY requirements.txt ./requirements.txt

# Frontend-specific dependencies
COPY frontend/requirements.txt ./frontend-requirements.txt

RUN pip install --no-cache-dir \
    -r requirements.txt \
    -r frontend-requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py"]