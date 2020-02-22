FROM python:alpine

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk add --update musl-dev gcc libffi-dev
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
RUN mv backend/ProductionEmailSender.py backend/EmailSender.py

CMD ["python3", "app.py"]
