FROM python:3.11.13-trixie
WORKDIR /mnt/hd/guess-songs
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "gunicorn" ]
CMD [ "--bind", "0.0.0.0:8000", "app:app"]
