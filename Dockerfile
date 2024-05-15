FROM python:3.12
# for caching  
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
cmd ["python3","main.py"] 

