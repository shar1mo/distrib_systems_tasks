.PHONY: proto up down logs test

proto:
	python -m grpc_tools.protoc -I proto --python_out=generated --grpc_python_out=generated proto/shipments/v1/shipments.proto

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

test:
	cd ../.. && GROUP=332 STUDENT_ID=s13 make test WEEK=17
