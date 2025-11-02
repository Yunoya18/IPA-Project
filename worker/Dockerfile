FROM python
WORKDIR /worker
COPY . /worker
RUN pip install -r requirements.txt
CMD ["python3", "-u", "consumer.py"]