FROM python:3.12-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential ffmpeg \
  && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app

# ✨ Ensure unbuffered logging
ENV PYTHONUNBUFFERED=1

# 🧠 Run unbuffered explicitly
CMD ["python", "-u", "consumer.py"]
