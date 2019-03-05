import json

class returnQuestions:
    def __init__(self, class_type, id, type, question):
        self.class_type = class_type
        self.id = id
        self.type = type
        self.question = question


question1 = returnQuestions("return_question", 5, "sa", "Hello?")

j = json.dumps(question1.__dict__)
print (j)

#print(j['class_type'])


q = json.loads(j)
question2 = returnQuestions(**q)

print (question2.id)

'''
json_string = '{"first_name": "Guido", "last_name":"Rossum"}'
parsed_json = json.loads(json_string)
print(parsed_json['first_name'])
'''
