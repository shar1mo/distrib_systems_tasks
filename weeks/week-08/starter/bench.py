import time
import requests
import grpc
import proto.service_pb2 as pb2
import proto.service_pb2_grpc as pb2_grpc

REST_URL = "http://localhost:8000/api/products"
GRPC_ADDRESS = "localhost:8243"

NUM_REQUESTS = 1000

def run_rest_bench():
    print("Starting REST benchmark...")
    start = time.time()
    for _ in range(NUM_REQUESTS):
        requests.get(REST_URL)
    end = time.time()
    print(f"REST: {end - start:.4f} sec")

def run_grpc_bench():
    print("Starting gRPC benchmark...")
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = pb2_grpc.ProductsServiceStub(channel)
        start = time.time()
        for _ in range(NUM_REQUESTS):
            stub.CreateProduct(pb2.CreateProductRequest(name="Test", price=1.0))
        end = time.time()
        print(f"gRPC Unary: {end - start:.4f} sec")

def run_grpc_stream_bench():
    print("Starting gRPC Server Streaming benchmark...")
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = pb2_grpc.ProductsServiceStub(channel)
        start = time.time()
        # получаем поток продуктов
        for product in stub.ListProductsStream(pb2.ListProductsRequest(limit=NUM_REQUESTS)):
            pass
        end = time.time()
        print(f"gRPC Server Streaming: {end - start:.4f} sec")

if __name__ == "__main__":
    run_rest_bench()
    run_grpc_bench()
    run_grpc_stream_bench()