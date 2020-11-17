FROM python:3.7.5-buster

RUN mkdir -p /var/local/app

COPY ./ /var/local/app/

WORKDIR /var/local/app

RUN pip install -r requirements.txt

EXPOSE 8090

ENV n='resources/test2jerky.json'

ENV w='.042'

CMD python main.py -n $n -p '8090' -w $w
