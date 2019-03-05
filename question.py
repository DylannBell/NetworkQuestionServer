import json, ssl, http.server, random, socketserver, threading

# Error catching for RestrictedPython module
try:
    from RestrictedPython import compile_restricted
    from RestrictedPython.Guards import safe_builtins
except ImportError as error:
    print(error)
    exit("You have not installed all the correct modules, "
         "please install RestrictedPython.")


PASSWORD = 'CITS3002'


class GenerateQuestions:
    def __init__(self, password, num_mc, num_short, num_long):
        self.password = password
        self.num_mc = num_mc
        self.num_short = num_short
        self.num_long = num_long


class ReturnQuestions:
    def __init__(self, q_id, question):
        self.q_id = q_id
        self.question = question


class RequestAnswer:
    def __init__(self, password, q_id, answer):
        self.password = password
        self.q_id = q_id
        self.answer = answer


class ReturnAnswer:
    def __init__(self, is_correct):
        self.is_correct = is_correct


class ServerHandler(http.server.BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
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


def check_password(post_request):
    if post_request["password"] == PASSWORD:
        return True
    else:
        return False


def run_restricted_python(code_to_run):

    # Run python code using RestrictedPython

    result = {}
    output = 0

    try:
        code = compile_restricted(code_to_run, '<string>', 'exec')
        exec(code, safe_builtins, result)

        # Run code with test case of 7
        output = (result['compute'](7))

    except:
        print("Error in attempting to run the code.")

    return output

def check_answer(answer_request):
    # FOR Q_ID: q1-20 = mcq, q21-40 = short answer, q41-50 = code


    # Open answer files and load into lists
    with open('MCQ_ANSWERS.txt') as f:
        mc_answers = f.read().splitlines()
    with open('SHORT_ANSWER_ANSWERS.txt') as f:
        short_answers = f.read().splitlines()
    with open('CODE_ANSWERS.txt') as f:
        long_answers = f.read().splitlines()

    # Load json string into class
    answer_request_class = RequestAnswer(**answer_request)

    # Check MCQ questions
    if answer_request_class.q_id in range(1, 21):
        correct_answer = mc_answers[answer_request_class.q_id - 1]

        if correct_answer == answer_request_class.answer:
            return_message_class = ReturnAnswer(True)
            return_answer = json.dumps(return_message_class.__dict__)
        else:
            return_message_class = ReturnAnswer(False)
            return_answer = json.dumps(return_message_class.__dict__)

    # Check short answer questions
    elif answer_request_class.q_id in range(21, 41):
        correct_answer = short_answers[answer_request_class.q_id - 21]

        #Try turn answer into an int
        try:
            answer = int(answer_request_class.answer)
        except TypeError:
            print("Did not receive an integer when expecting one.")
            answer=0

        if int(correct_answer) == answer:
            return_message_class = ReturnAnswer(True)
            return_answer = json.dumps(return_message_class.__dict__)
        else:
            return_message_class = ReturnAnswer(False)
            return_answer = json.dumps(return_message_class.__dict__)

    # Check code questions
    elif answer_request_class.q_id in range(41, 51):
        correct_answer = long_answers[answer_request_class.q_id - 41]
        answer = run_restricted_python(answer_request_class.answer)

        if int(correct_answer) == answer:
            return_message_class = ReturnAnswer(True)
            return_answer = json.dumps(return_message_class.__dict__)
        else:
            return_message_class = ReturnAnswer(False)
            return_answer = json.dumps(return_message_class.__dict__)

    else:
        print("Question id is incorrect.")

    return return_answer


def generate_questions(generate_questions_request):
    # Generate a certain amount of mc, short and long answer questions
    # Message is going to be a json string of json strings.

    generate_questions_class = GenerateQuestions(**generate_questions_request)

    number_mcq = generate_questions_class.num_mc
    number_short = generate_questions_class.num_short
    number_long = generate_questions_class.num_long

    # Load text files into lists
    with open('MCQ_QUESTIONS.txt') as f:
        mc_questions = f.read().splitlines()
    with open('SHORT_ANSWER_QUESTIONS.txt') as f:
        short_questions = f.read().splitlines()
    with open('CODE_QUESTIONS.txt') as f:
        long_questions = f.read().splitlines()

    # Initialise list which is going to contain json strings
    return_questions = '['

    # Initialise lists which contain the q_ids.
    list_of_mc_questions = list(range(0, 19))
    list_of_short_questions = list(range(20, 39))
    list_of_long_questions = list(range(40, 49))

    # Add multiple choice Questions
    while number_mcq > 0:
        if number_mcq > 0 and len(list_of_mc_questions) > 0:
            # Generate a random number
            random_number = random.randint(0, len(list_of_mc_questions) - 1)
            q_id = list_of_mc_questions[random_number - 1]

            # Add question to list of questions
            question_class = ReturnQuestions(q_id + 1, mc_questions[q_id])
            question_json = json.dumps(question_class.__dict__)
            return_questions += (question_json + ', ')

            # Remove that question so no duplicates
            list_of_mc_questions.remove(q_id)
            number_mcq = number_mcq - 1

    # Add short answer questions
    while number_short > 0:
        if number_short > 0 and len(list_of_short_questions) > 0:
            # Generate a random number
            random_number = random.randint(0, len(list_of_short_questions) - 1)
            q_id = list_of_short_questions[random_number - 1]

            # Add question to list of questions
            question_class = ReturnQuestions(q_id, short_questions[q_id - 21])
            question_json = json.dumps(question_class.__dict__)
            return_questions += (question_json + ', ')

            # Remove that question so no duplicates
            list_of_short_questions.remove(q_id)
            number_short = number_short - 1

    # Add code questions
    while number_long > 0:
        if number_long > 0 and len(list_of_long_questions) > 0:

            # Generate a random number
            random_number = random.randint(0, len(list_of_long_questions) - 1)
            q_id = list_of_long_questions[random_number - 1]

            # Add question to list of questions
            question_class = ReturnQuestions(q_id, long_questions[q_id - 41])
            return_questions += json.dumps(question_class.__dict__)

            # Remove that question so no duplicates
            list_of_long_questions.remove(q_id)
            number_long = number_long - 1

            # If this is the last question, then close the json string
            if number_long == (number_long - 1):
                return_questions += ']'
            else:
                return_questions += ', '

    return return_questions


def generate_request(post_request):
    print("Request received from " + post_request.client_address[0]
          + ":" + str(post_request.client_address[1]) + ".")

    # Get the body from POST request and load it into json string
    #try:
    message_length = int(post_request.headers['Content-Length'])
    received_request = post_request.rfile.read(message_length)
    received_request = received_request.decode('utf8')
    print("Request = " + received_request)
    json_received_request = json.loads(received_request)

    try:
        if check_password(json_received_request):
            print("Password match, continuing.")

            # Get the request type from the url path and strip it
            request_type = post_request.path[1:].rstrip()
            print("Request = " + request_type + ".")

            if request_type == 'request_questions':
                generated_request = generate_questions(json_received_request)
            elif request_type == 'request_answer':
                generated_request = check_answer(json_received_request)

        else:
            generated_request="Password incorrect, request denied."

    except:
        print("Did not receive a correctly formatted json string")
        generated_request="Incorrectly formatted json string."


    return generated_request


def start_server():
    server_address = ('', 5555)

    #Thread each request so it can handle multiple at a time.
    http_server = ThreadedHTTPServer(server_address, ServerHandler)

    # Wrap socket in ssl and perform handshake on connection.
    http_server.socket = ssl.wrap_socket(http_server.socket,
                                         server_side=True,
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
