import json, ssl, http.server, random, javabridge, multiprocessing
from threading import Thread
#import os

#Does the server know what it's receiving or should we double check it's
#the right type of thing every time?
#What if it's greater than the max buffer size?
#Need a way to shutdown server
#What does httpd.serve_forever() do?
#Need to do coding questions
#Need to make sure javabridge is safe.

KEYFILE = 'server.key'
CERTFILE = 'server.crt'
MAX_BUFFER_SIZE = 4096

class returnQuestions:
    def __init__(self, id, question):
        self.id = id
        self.question = question

class requestAnswer:
    def __init__(self, id, answer):
        self.id = id
        self.answer = answer

class returnAnswer:
    def __init__(self, is_correct):
        self.is_correct = is_correct

class requestQuestions:

def run_javabridge(java_code_to_run):
    javabridge.start_vm(run_headless=True)
    try:
        output = javabridge.run_script(java_code_to_run)
        print(output)

        # need to process and return some stuff here
        
    finally:
        javabridge.kill_vm()


def generate_questions():
    #5 mcq, 3 short answer, 2 code questions
    #message is going to be a json string of json strings.

    #Load text files into lists
    with open('MCQ_QUESTIONS.txt') as f:
        MCQ_QUESTIONS = f.read().splitlines()

    with open('SHORT_ANSWER_QUESTIONS.txt') as f:
        SHORT_ANSWER_QUESTIONS= f.read().splitlines()

    with open('CODE_QUESTIONS.txt') as f:
        CODE_QUESTIONS = f.read().splitlines()    

    #Initialise json string
    return_questions = '{'

    #Add MCQ Questions
    for i in range(5):
        random_number = random.randint(0,19)
        question_class = returnQuestions("return_questions",
                                         random_number+1,
                                         MCQ_QUESTIONS[random_number])
        question_json = json.dumps(question_class.__dict__)
        return_questions += question_json
        return_questions += ', '

    #Add short answer questions
    for i in range(3):
        random_number = random.randint(0,19)
        question_class = returnQuestions("return_questions",
                                         random_number+21,
                                         SHORT_ANSWER_QUESTIONS[random_number])
        question_json = json.dumps(question_class.__dict__)
        return_questions += question_json
        return_questions += ', '

    #Add code questions
    for i in range(2):
        random_number = random.randint(0,9)
        question_class = returnQuestions("return_questions",
                                          random_number + 41,
                                          CODE_QUESTIONS[random_number])

        #If this is the last question, then close the json string
        
        if i == 1:
            return_questions += json.dumps(question_class.__dict__)
            return_questions += '}'
        else:
            return_questions += json.dumps(question_class.__dict__)
            return_questions += ', '
    
    print (return_questions)
    return return_questions

def check_answer(answer_request):
    # FOR ID: q1-20 = mcq, q21-40 = short answer, q41-50 = code

    with open('MCQ_ANSWERS.txt') as f:
        MCQ_ANSWERS = f.read().splitlines()

    with open('SHORT_ANSWER_ANSWERS.txt') as f:
        SHORT_ANSWER_ANSWERS = f.read().splitlines()

    with open('CODE_ANSWERS.txt') as f:
        CODE_ANSWERS = f.read().splitlines()    
    
    #load json string into class
    answer_request_class = requestAnswer(**json.loads(answer_request))

    #Check MCQ questions
    if answer_request_class.id in range(1,21):
        correct_answer = MCQ_ANSWERS[answer_request_class.id-1]
        if correct_answer == answer_request_class.answer:
            return_message_class = returnAnswer(True)
            return_message = json.dumps(return_message_class.__dict__)
        else:
            return_message_class = returnAnswer(False)
            return_message = json.dumps(return_message_class.__dict__)

    #Check short answer questions
    elif answer_request_class.id in range(21,41):
        correct_answer = SHORT_ANSWER_ANSWERS[answer_request_class.id-21]
        if correct_answer == answer_request_class.answer:
            return_message_class = returnAnswer(True)
            return_message = json.dumps(return_message_class.__dict__)
        else:
            return_message_class = returnAnswer(False)
            return_message = json.dumps(return_message_class.__dict__)

    #Check code questions
    elif answer_request_class.id in range(41,51):
        #Time process and kill it if it's too long

        # Start run_java as a process
        p = multiprocessing.Process(target=run_javabridge('java.lang.String.format("Hello, World!");'))
        p.start()
    
        # Wait for 10 seconds or until process finishes
        p.join(10)
    
        # If thread is still active
        if p.is_alive():
            print ("running... let's kill it...")
    
            # Terminate
            p.terminate()
            p.join()

    else:
        print ("Question id is incorrect.")

    return return_message

def generate_request(received_request):
    #Turn string into json
    print(received_request)
    json_received_request = json.loads(received_request)
    
    if json_received_request['class_type'] == 'request_questions':
        return_message = generate_questions()
    elif json_received_request['class_type'] == 'request_answer':
        return_message = check_answer(received_request)

    return return_message

def request_thread(conn):

    #Receive a request
    received_request = conn.recv(MAX_BUFFER_SIZE)
    received_request = received_request.decode("utf8").rstrip() #strips EOL
    
    #Generate request
    return_message = generate_request(received_request)
    
    #Send the generated request
    conn.send(return_message.encode("utf8"))

    #Close connection 
    conn.close()
    #print('Connection ' + ip + ':' + port + " has been closed.")

def start_server():

    #Create https server
    server_address = ('localhost', 12345)
    httpd = http.server.HTTPServer(server_address,
                                   http.server.SimpleHTTPRequestHandler)

    '''
        httpd.socket = ssl.wrap_socket(httpd.socket,
                                       server_side=False,
                                       cert_reqs=ssl.CERT_NONE,
                                       ssl_version=ssl.PROTOCOL_TLSv1)
                                       
    '''
    '''
        server side = true
        keyfile = 'server.key',
        certfile = 'server.crt',
    '''

    print('Socket created.')

    #httpd.serve_forever() ???
    print('Socket is now waiting for requests.')

    #Infinite loop while waiting for connection
    try:
        while True:

            #Connection found

            print ("getting here")
            conn, addr = httpd.socket.accept()
            print ("Getting here 2")
            ip, port = str(addr[0]), str(addr[1])

            print('Accepting connection from ' + ip + ':' + port)

            try:
                #start a thread
                print ("Thread created.")
                #Thread(target=request_thread, args=(conn, ip, port)).start()
                Thread(target=request_thread, args=(conn)).start()

            except:
                #error in threading
                print("An error occured when trying to create a thread.")
                import traceback
                traceback.print_exc()

    except KeyboardInterrupt:
        print ("Keyboard interrupt. Server will not be closed.")
        httpd.socket.close()
        print("Server has been closed")

start_server()