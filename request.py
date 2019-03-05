import socket
import json
import random
import ssl

MAX_BUFFER_SIZE = 4096

'''

sizeOfInput = sys.getsizeof(input_from_client_bytes)
if  sizeOfInput >= MAX_BUFFER_SIZE:
    print("The length of input is probably too long: {}".format(siz))

'''


def connect_to_server():
    # Connecting to the socket and port
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_soc = ssl.wrap_socket(soc, cert_reqs=ssl.CERT_NONE, ca_certs='server.crt')
    ssl_soc.connect(("127.0.0.1", 12345))
    return ssl_soc


def main():
    ssl_soc = connect_to_server()

    # message
    # message_to_send = '{"class_type": "request_answer", "id": 21, "answer": "Dylan"}'
    # message_to_send = '{"class_type": "request_questions"}'
    message_to_send = '{"class_type": "request_answer", "id": 42, "answer": "some code"}'

    # Send a message
    ssl_soc.send(message_to_send.encode("utf8"))

    # Receive a question/answer request
    request_bytes = ssl_soc.recv(MAX_BUFFER_SIZE)
    request_string = request_bytes.decode("utf8")

    print(request_string)

    '''
    rq = json.loads(request_string)
    if rq['is_correct']:it
        print ("success")
    '''


if __name__ == "__main__":
    main()
