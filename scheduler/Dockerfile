FROM python
WORKDIR /scheduler
COPY . /scheduler
RUN pip install -r requirements.txt
CMD ["python3", "-u", "scheduler.py"]