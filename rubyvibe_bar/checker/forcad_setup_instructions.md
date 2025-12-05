# Изменить файл `docker_config/celery/Dockerfile` в ForcAD чтобы установить Playwright

```
FROM python:3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=${PYTHONPATH}:/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY docker_config/await_start.sh /await_start.sh
COPY docker_config/db_check.py /db_check.py
COPY docker_config/check_initialized.py /check_initialized.py

RUN chmod +x /await_start.sh

###### SHARED PART END ######

########## CUSTOMIZE ##########

ENV PWNLIB_NOTERM=true

COPY ./checkers/requirements.txt /checker_requirements.txt
RUN pip install -r /checker_requirements.txt

##########################
# Playwright installation
##########################
# Where Playwright will store browsers (shared for all users)
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN mkdir -p /ms-playwright
RUN playwright install chromium --with-deps

COPY ./checkers /checkers

########## END CUSTOMIZE ##########

COPY backend /app

COPY ./docker_config/celery/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /home/nobody \
    && chown -R nobody:nogroup /home/nobody /ms-playwright /app

ENV HOME=/home/nobody

USER nobody

CMD ["/entrypoint.sh"]
```

## Пример config.yml
```
tasks:
- checker: vibe_ruby/checker.py
  checker_timeout: 30
  checker_type: hackerdom
  gets: 5
  name: 'RubyVibe Bar (3000)'
  places: 2
  puts: 2
```
