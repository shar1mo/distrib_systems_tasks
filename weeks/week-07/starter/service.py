import grpc
from concurrent import futures
import uuid

# Импортируем сгенерированные файлы
import proto.service_pb2 as pb2
import proto.service_pb2_grpc as pb2_grpc

# Реализация сервиса
class ProductsServiceServicer(pb2_grpc.ProductsServiceServicer):
    def CreateProduct(self, request, context):
        # Создаем "новый продукт"
        product_id = str(uuid.uuid4())
        response = pb2.CreateProductResponse(
            id=product_id,
            name=request.name,
            price=request.price
        )
        print(f"Created product: {response}")
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ProductsServiceServicer_to_server(ProductsServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC server is running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()