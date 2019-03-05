import json, ssl, http.server, random, socketserver, threading
# Error catching for RestrictedPython module
try:
    from RestrictedPython import compile_restricted
    from RestrictedPython.Guards import safe_builtins
except ImportError as error:
    print(error)
    exit("You have not installed all the correct modules, "
         "please install RestrictedPython.")


# Does the server know what it's receiving or should we double check it's
# the right type of thing every time?
# What headers need to be included in the post request?
# Error requests ?
# Need to fix run_python_code by using a common function name


class GenerateQuestions:
    def __init__(self, num_mc, num_short, num_long):
        self.num_mc = num_mc
        self.num_short = num_short
        self.num_long = num_long


class ReturnQuestions:
    def __init__(self, q_id, question):
        self.q_id = q_id
        self.question = question


class RequestAnswer:
    def __init__(self, q_id, answer):
        self.id = q_id
        self.answer = answer


class ReturnAnswer:
    def __init__(self, is_correct):
        self.is_correct = is_correct


class ServerHandler(http.server.BaseHTTPRequestHandler):

    def _set_headers(self):
        # Need to change headers
        self.send_response(200)  # What does this number mean?
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        return_message = generate_request(self)
        self._set_headers()
        self.wfile.write(return_message.encode('utf8'))

    # This is for testing connection and threading
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        message = threading.currentThread().getName()
        self.wfile.write(message.encode('utf8'))
        self.wfile.write(b'\n')
        return


class ErrorHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_error(404)
        return


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    # Handle requests in a separate thread.
    pass


def run_restricted_python(code_to_run):
    # Run python code using RestrictedPython

    result = {}
    """
    code_to_run = '''
    def do_some_stuff():
        i = 1
        return i]
    """

    try:
        code = compile_restricted(code_to_run, '<string>', 'exec')
        exec(code, safe_builtins, result)

        # Need to change function name
        output = (result['question']())

    except:
        print("Error in attempting to run the code.")

    print(output)
    return output


def check_answer(answer_request):
    # FOR ID: q1-20 = mcq, q21-40 = short answer, q41-50 = code

    # Open answer files and load into lists
    with open('MC_ANSWERS.txt') as f:
        mc_answers = f.read().splitlines()
    with open('SHORT_ANSWER_ANSWERS.txt') as f:
        short_answers = f.read().splitlines()
    with open('CODE_ANSWERS.txt') as f:
        long_answers = f.read().splitlines()

    # Load json string into class
    answer_request_class = RequestAnswer(**answer_request)

    # Check MCQ questions
    if answer_request_class.id in range(1, 21):
        correct_answer = mc_answers[answer_request_class.id - 1]

        if correct_answer == answer_request_class.answer:
            return_message_class = ReturnAnswer(True)
            return_message = json.dumps(return_message_class.__dict__)
        else:
            return_message_class = ReturnAnswer(False)
            return_message = json.dumps(return_message_class.__dict__)

    # Check short answer questions
    elif answer_request_class.id in range(21, 41):
        correct_answer = short_answers[answer_request_class.id - 21]

        if correct_answer == answer_request_class.answer:
            return_message_class = ReturnAnswer(True)
            return_message = json.dumps(return_message_class.__dict__)
        else:
            return_message_class = ReturnAnswer(False)
            return_message = json.dumps(return_message_class.__dict__)

    # Check code questions
    elif answer_request_class.id in range(41, 51):
        correct_answer = long_answers[answer_request_class.id - 41]
        answer = run_restricted_python(answer_request_class.answer)

        if correct_answer == answer:
            return_message_class = ReturnAnswer(True)
            return_message = json.dumps(return_message_class.__dict__)
        else:
            return_message_class = ReturnAnswer(False)
            return_message = json.dumps(return_message_class.__dict__)

    else:
        print("Question id is incorrect.")
        # Maybe send an error here?

    return return_message


def generate_questions(generate_questions_request):
    # Generate a certain amount of mc, short and long answer questions
    # Message is going to be a json string of json strings.

    generate_questions_class = GenerateQuestions(**generate_questions_request)

    number_mcq = generate_questions_class.num_mc
    number_short = generate_questions_class.num_short
    number_long = generate_questions_class.num_long

    # Load text files into lists
    with open('MCQ_QUESTIONS.txt') as f:
        MCQ_QUESTIONS = f.read().splitlines()
    with open('SHORT_ANSWER_QUESTIONS.txt') as f:
        SHORT_QUESTIONS = f.read().splitlines()
    with open('CODE_QUESTIONS.txt') as f:
        LONG_QUESTIONS = f.read().splitlines()

    # Initialise list which is going to contain json strings
    return_questions = '['

    #Initialise lists which contain the q_ids.
    list_of_mc_questions = list(range(0, 19))
    list_of_short_questions = list(range(20, 39))
    list_of_long_questions = list(range(40, 49))

    print(list_of_mc_questions)
    print (list_of_short_questions)
    # Add multiple choice Questions

    while number_mcq > 0:
        if number_mcq > 0 and len(list_of_mc_questions) > 0:
            # Generate a random number
            random_number = random.randint(0, len(list_of_mc_questions)-1)
            q_id = list_of_mc_questions[random_number - 1]

            # Add question to list of questions
            question_class = ReturnQuestions(q_id + 1, MCQ_QUESTIONS[q_id])
            question_json = json.dumps(question_class.__dict__)
            return_questions += (question_json + ', ')

            # Remove that question so no duplicates
            list_of_mc_questions.remove(q_id)
            print("getting here")
            number_mcq = number_mcq - 1

    # Add short answer questions

    while number_short > 0:
        if number_short > 0 and len(list_of_short_questions) > 0:

            # Generate a random number
            random_number = random.randint(0, len(list_of_short_questions)-1)
            q_id = list_of_short_questions[random_number - 1]

            # Add question to list of questions
            print(q_id)
            print(SHORT_QUESTIONS)
            question_class = ReturnQuestions(q_id, SHORT_QUESTIONS[q_id-21])
            question_json = json.dumps(question_class.__dict__)
            return_questions += (question_json + ', ')

            # Remove that question so no duplicates
            list_of_short_questions.remove(q_id)
            number_short = number_short - 1


        # Old code
        '''
        random_number = random.randint(0, 19)
        question_class = ReturnQuestions(random_number + 21,
                                         SHORT_ANSWER_QUESTIONS[random_number])
        question_json = json.dumps(question_class.__dict__)
        return_questions += question_json
        return_questions += ', '
        '''

    # Add code questions
    while number_long > 0:
        if number_long > 0 and len(list_of_long_questions) > 0:

            # Generate a random number
            random_number = random.randint(0, len(list_of_long_questions)-1)
            q_id = list_of_long_questions[random_number - 1]

            # Add question to list of questions
            question_class = ReturnQuestions(q_id, LONG_QUESTIONS[q_id-41])
            return_questions += json.dumps(question_class.__dict__)

            # If this is the last question, then close the json string
            if number_long == (number_long - 1):
                return_questions += ']'
            else:
                return_questions += ', '

            # Remove that question so no duplicates
            list_of_long_questions.remove(q_id)
            number_long = number_long - 1


    print(return_questions)
    return return_questions


def generate_request(post_request):
    print(post_request.client_address)  # This is the ip and port
    print(post_request.path)  # This is url

    # Get the body from POST request and load it into json string
    message_length = int(post_request.headers['Content-Length'])
    received_request = post_request.rfile.read(message_length).decode('utf8')
    print("json req = " + received_request)
    json_received_request = json.loads(received_request)



    # Get the request type from the path and strip it of
    request_type = post_request.path[1:].rstrip()
    print("Request = " + request_type + ".")

    if request_type == 'request_questions':
        generated_request = generate_questions(json_received_request)
    elif request_type == 'request_answer':
        generated_request = check_answer(json_received_request)

    return generated_request


def start_server():
    server_address = ('localhost', 5555)
    http_server = ThreadedHTTPServer(server_address, ServerHandler)

    # Wrap socket in ssl and perform handshake on connection.
    http_server.socket = ssl.wrap_socket(http_server.socket,
                                         server_side=True,  # cert_reqs=ssl.CERT_REQUIRED,
                                         keyfile='server.key',
                                         certfile='server.crt',
                                         ssl_version=ssl.PROTOCOL_TLSv1)

    print('HTTPS Server created.')
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt, server has been closed.")
        http_server.server_close()


if __name__ == "__main__":
    start_server()
