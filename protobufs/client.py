import grpc
import calculator_pb2
import calculator_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = calculator_pb2_grpc.CalculatorStub(channel)

def call_add():
    response = stub.Add(calculator_pb2.AddRequest(number1=10, number2=50))
    print("Add Result: " + str(response.result))

def call_Multiply():
    response = stub.Multiply(calculator_pb2.MultiplyRequest(input1=6, input2=6))
    print("Multiply Result: " + str(response.result))

if __name__ == '__main__':
    call_add()
    call_Multiply()
