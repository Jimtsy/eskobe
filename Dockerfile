FROM python:3.6-alpine

WORKDIR /eskobe
VOLUME /eskobe/logs
ADD . /eskobe/
RUN pip install --no-cache -U -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt