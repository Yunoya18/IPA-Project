FROM python
WORKDIR /web
COPY . /web
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python3", "app.py"]