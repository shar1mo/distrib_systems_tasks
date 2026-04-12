import grpc
from concurrent import futures
import uuid
import time

import proto.service_pb2 as pb2
import proto.service_pb2_grpc as pb2_grpc

# Хранилище продуктов (для примера)
PRODUCTS_DB = []

class ProductsServiceServicer(pb2_grpc.ProductsServiceServicer):
    def CreateProduct(self, request, context):
        product_id = str(uuid.uuid4())
        product = pb2.CreateProductResponse(
            id=product_id,
            name=request.name,
            price=request.price
        )
        PRODUCTS_DB.append(product)
        print(f"Created product: {product}")
        return product

    def ListProductsStream(self, request, context):
        count = 0
        for product in PRODUCTS_DB:
            if count >= request.limit:
                break
            # Имитируем задержку для наглядности стрима
            time.sleep(0.01)
            yield pb2.Product(
                id=product.id,
                name=product.name,
                price=product.price
            )
            count += 1

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ProductsServiceServicer_to_server(ProductsServiceServicer(), server)
    server.add_insecure_port('[::]:8243')  # порт из вашего варианта
    print("gRPC server is running on port 8243...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()