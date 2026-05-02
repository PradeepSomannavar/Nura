FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY vectorstore/ vectorstore/
COPY data/ data/

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1

EXPOSE 8501

HEALTHCHECK CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"]

ENTRYPOINT ["python", "-m", "medibot.cli", "web"]
