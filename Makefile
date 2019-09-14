version = 0.1
container = "gft-ner-service"

protocGenerate:
	rm -rf generated
	mkdir -p generated
	python -m grpc_tools.protoc -I ./gft-proto/ner-service/ --python_out=./generated/ --grpc_python_out=./generated/ ./gft-proto/ner-service/ner.proto
	ls generated | xargs -I {} sed -i 's/import \([a-zA-Z0-9]*\)_pb2/import generated\.\1_pb2/g'  generated/{}


build:
	docker build . -t docker.codeheroes.io/$(container):$(version)

publish: build
	docker push docker.codeheroes.io/$(container):$(version)

run:
	docker run --rm -p 8080:8080 docker.codeheroes.io/$(container):$(version)

run_sh:
	docker run --rm -it  --entrypoint /bin/sh  docker.codeheroes.io/$(container):$(version)
