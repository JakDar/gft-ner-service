FROM python:3.7-slim

RUN python -m pip install pip --upgrade
RUN python -m pip install wheel

RUN python -m pip install grpcio-tools==1.22.0
RUN python -m pip install pyfunctional
RUN python -m pip install spacy==2.1.8
RUN python -m spacy download en_core_web_lg

RUN mkdir -p /app/generated

ADD ./gft-proto /app/gft-proto
ADD *.py /app/

RUN python -m grpc_tools.protoc -I /app/gft-proto/ner-service/ --python_out=/app/generated/ --grpc_python_out=/app/generated/ /app/gft-proto/ner-service/ner.proto
RUN ls /app/generated | xargs -I {} sed -i 's/import \([a-zA-Z0-9]*\)_pb2/import generated\.\1_pb2/g'  /app/generated/{}

CMD python /app/main.py
