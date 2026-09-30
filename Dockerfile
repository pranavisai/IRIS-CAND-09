
FROM python:3.12-slim

WORKDIR /iris-cand-09

ENV PYTHONPATH=/iris-cand-09
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . /iris-cand-09/

RUN mkdir -p /iris-cand-09/output /iris-cand-09/logs \
    && ln -s /iris-cand-09/logs /var/log/iris-cand-09 \
    && groupadd --system iris \
    && useradd --system --gid iris --home-dir /iris-cand-09 \
       --no-create-home iris \
    && chown -R iris:iris /iris-cand-09/output /iris-cand-09/logs

USER iris

CMD ["python", "-m", "app.worker"]