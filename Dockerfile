FROM python:3.8-alpine AS builder

WORKDIR /app

COPY . .

RUN apk add --no-cache openssl-dev libffi-dev build-base && pip install --no-cache-dir build
RUN pip install . && python -mbuild

FROM python:3.8-alpine

RUN addgroup -S app && adduser -S app -G app

RUN apk add --no-cache uwsgi uwsgi-python3 nginx

WORKDIR /app
COPY server.crt /app/ssl/cert.pem
COPY server.key /app/ssl/cert.key
COPY supervisord.conf /app/supervisord.conf
COPY nginx.conf /app/nginx.conf
COPY uwsgi.ini /app/uwsgi.ini
COPY --from=builder  /app/dist/phonecheck-0.0.0.tar.gz .
RUN  pip install phonecheck-0.0.0.tar.gz supervisor && rm phonecheck-0.0.0.tar.gz && chown -R app:app /app

CMD [ "supervisord", "-n", "-c", "/app/supervisord.conf"]


