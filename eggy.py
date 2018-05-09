import spacy
import spacy.symbols as symbols

def start_state(token, attributes):
    pass

def handle_question(token, attributes):
    attributes["question"] = token.text

def handle_command(token, attributes):
    attributes["command"] = token.text

def state_determiner(token, attributes):
    pass

def get_object_to_search(token, attributes):
    attributes["object_of_search"] = token
    if token.tag_ == "NN":
        attributes["object_of_search_qty"] = "singular"
    else:
        attributes["object_of_search_qty"] = "plural"

def get_search_criteria(token, attributes):
    attributes["current_criteria"] = token.lemma_
    if "criteria" not in attributes:
        attributes["criteria"] = {}
    attributes["criteria"][token.lemma_] = {}
    attributes["criteria"][token.lemma_]["degree"] = "equals"
    attributes["criteria"][token.lemma_]["value"] = []
    print("children")

def state_search_criteria_value(token, attributes):
    if "current_criteria" in attributes and attributes["current_criteria"] != "":
        if "current_value" not in attributes:
            attributes["current_value"] = 0
        attributes["criteria"][attributes["current_criteria"]]["value"].append(token.text)
        attributes["current_value"] += 1

def state_location(token, attributes):
    attributes["location"] = {}

def get_location(token, attributes):
    for child in token.children:
        print(child, child.dep_)
        if child.dep_ == "pobj":
            attributes["location"] = {}
            attributes["location"]["value"] = child.text

def state_location_value(token, attributes):
    attributes["location"]["value"] = token.text
    
def handle_aux_verb(token, attributes):
    pass

def handle_conjunction(token, attributes):
    for child in token.children:
        print(child, child.dep_)

def process_location_determiner(token, attributes):
    attributes["location"]["description"] = token.text

def process_conjunction(token, attributes):
    for child in token.children:
        print(child, child.dep_)

def process_conjuncted_criteria(token, attributes):
    if "current_criteria" in attributes and attributes["current_criteria"] != "":
        if "current_value" not in attributes:
            attributes["current_value"] = 0
        attributes["criteria"][attributes["current_criteria"]]["value"].append(token.text)
        attributes["current_value"] += 1

def process_wh_criteria(token, attributes):
    for child in token.children:
        print(child, child.dep_)

def process_wh_det_criteria(token, attributes):
    for child in token.children:
        print(child, child.dep_)

def process_wh_be(token,attributes):
    for child in token.children:
        print(child, child.dep_)

def process_adj_criteria(token, attributes):
    get_search_criteria(token, attributes)
    for child in token.children:
        print(child, child.dep_)
        if child.dep_ == "prep":
            attributes["criteria"][token.lemma_]["degree"] = child.text

def process_degree(token, attributes):
    pass

def process_size(token, attributes):
    if "current_value" not in attributes:
        attributes["current_value"] = 0

    attributes["criteria"][attributes["current_criteria"]]["value"].append({"value" : token.text})
    attributes["current_value"] += 1

def process_measurement(token, attributes):
    attributes["criteria"][attributes["current_criteria"]]["value"][0]["quantity"] = token.text

states = {
            #wh-questions
            start_state: [
                            (lambda token: token.tag_ == "WP", handle_question),
                            (lambda token: token.tag_ == "WDT", handle_question),
                            (lambda token: token.tag_ == "VB", handle_command),
                            (lambda token: token.text in ['list'], handle_command),
                         ],
            handle_question: [ 
                                (lambda token: token.pos_ == "NOUN", get_object_to_search),
                             ],
            handle_command: [
                                (lambda token: token.pos_ == "NOUN", get_object_to_search),
                                (lambda token: token.pos_ == "DET", state_determiner),
                ],
            state_determiner: [
                                (lambda token: token.pos_ == "NOUN", get_object_to_search),
                ],
            get_object_to_search: [
                                    (lambda token: token.pos_ == "VERB" and token.lemma_ != "be", get_search_criteria),
                                    (lambda token: token.lemma_ == "be", process_wh_be),
                                    (lambda token: token.dep_ == "prep", state_location),
                                    (lambda token: token.tag_ == "WP$", process_wh_criteria),
                                    (lambda token: token.tag_ == "WDT", process_wh_det_criteria),
                                    (lambda token: token.tag_ == "JJR", process_adj_criteria),
                                  ],
            get_search_criteria: [
                                    (lambda token: True, state_search_criteria_value),
                                    #(lambda token: token.pos_ == "NOUN", state_search_criteria_value),
                                    #(lambda token: token.pos_ == "PROPN", state_search_criteria_value),
                                 ],
            state_search_criteria_value : [
                                            (lambda token: token.tag_ == "CC", process_conjunction),
                                            (lambda token: token.tag_ == "IN", state_location),
                                        ],
            state_location : [
                              (lambda token: token.pos_ == "NOUN", state_location_value),
                              (lambda token: token.pos_ == "DET", process_location_determiner),
                           ],
            state_location_value : [
                                        (lambda token: token.pos_ == "VERB", get_search_criteria),
                                        (lambda token: token.tag_ == "WP$", process_wh_criteria),
                                        (lambda token: token.tag_ == "WDT", process_wh_det_criteria)
                                   ],
            process_location_determiner : [
                                            (lambda token: token.pos_ == "NOUN", state_location_value),
                                          ],
            process_conjunction : [
                                    (lambda token: token.pos_ == "NOUN", process_conjuncted_criteria),
                                    (lambda token: token.tag_ == "JJR", process_adj_criteria),
                ],
            process_conjuncted_criteria: [
                        (lambda token: token.tag_ == "WP$", process_wh_criteria),
                        (lambda token: token.tag_ == "WDT", process_wh_det_criteria)
                ],
            process_wh_criteria : [
                ],
            process_wh_det_criteria : [
                    (lambda token: token.lemma_ == "be", process_wh_be),
                ],
            process_wh_be: [
                    (lambda token: token.tag_ == "JJR", process_adj_criteria),
                    (lambda token: token.pos_ == "VERB" and token.dep_ == "relcl", get_search_criteria),
                ],
            process_adj_criteria: [
                    (lambda token: token.dep_ == "prep" and token.pos_ == "ADP", process_degree),
                    (lambda token: token.dep_ == "quantmod" and token.pos_ == "ADP", process_degree)
                ],
            process_degree : [
                    (lambda token: token.dep_ == "nummod", process_size)
                    ],
            process_size: [
                    (lambda token: token.dep_ == "pobj", process_measurement)
                    ],
            process_measurement: [
                    ],

         }


def main():
    nlp = spacy.load('en_core_web_sm')
    #analyze(input("input command here:"), nlp)
    #analyze("show me all files", nlp)
    print("-------------------------------------")
    #attributes = analyze("show all files in this directory named bla", nlp)
    #print(get_command_string(attributes, True))
    #analyze("list all files", nlp)
    #attributes = analyze("show all files containing hi and dada", nlp)
    #print(get_command_string(attributes, True))

    attributes = analyze("list all files named larger in pycharm", nlp)
    print(attributes)
    print(get_command_string(attributes))
    #analyze("show all files which are named filename and larger than 3 kilobytes", nlp)
    #analyze("what file contains bla.txt", nlp)
    #analyze("what file in hello contains bla.txt", nlp)
    #analyze("what file in this directory containing bla.txt", nlp)
    #analyze("what files contain bla and foo which are larger than 3 kilobytes", nlp)
    #analyze("what files contain bla", nlp)
    #analyze("which files are larger than 3 kilobytes", nlp)
    #analyze("show files larger than 3 kilobytes", nlp)
    #analyze("show all files in this directory", nlp)
    #analyze("show all files", nlp)
    
def analyze(the_text, nlp):
    text = (the_text)
    doc = nlp(text)
    current_state = start_state
    attributes = {"isComplete" : True}

    for token in doc:
        print("token = %s, lemma = %s, norm = %s, pos = %s, tag = %s, tag_ = %s, dep = %s" % (token.text, token.lemma_, token.norm_, token.pos_, 
            token.tag_, spacy.explain(token.tag_), token.dep_))
        
        next_state = None
        for state in states[current_state]:
            if state[0](token):
                next_state = state
                break

        print(next_state)
        
        if next_state == None:
            print("i have reached the end!", token)
            attributes["isComplete"] = False
            break
        current_state = next_state[1]

        current_state(token, attributes)

    print("***********************")
    print(attributes)
    print("***********************")

    return attributes

    """
    print("***********************")
    for token in doc:
        print("###############################")
        print("token = %s, lemma = %s, norm = %s, pos = %s, tag = %s, tag_ = %s, dep = %s" % (token.text, token.lemma_, token.norm_, token.pos_, 
            token.tag_, spacy.explain(token.tag_), token.dep_))
        print(spacy.explain(token.tag_))
        for child in token.children:
            print(child.text, child.dep_)
        print("###############################")

        if token.pos == symbols.VERB:
            if token.tag_ == "VB":
                print("command: %s" % token.text)
                attributes["command"] = token.text
                attributes["command_obj"] = get_direct_object(token)
            else:
                attributes["criteria"] = {}
                attributes["criteria"][token.text] = get_direct_object(token)
        if token.pos == symbols.ADJ:
            pass

    print(attributes)
    print("*****************")
    """
        

def get_command_string(attributes):
    if not attributes["isComplete"]:
        print("sorry, i can't process your request") 
        return None

    if "command" in attributes:
        command = attributes["command"]

        if command in ["show", "give", "list"]:
            for criterium, info in attributes["criteria"].items():
                if criterium == "contain":
                    command = "ack \'"

                    if info["degree"] == "equals":
                        for i in range(0, len(info["value"])):
                            command = command + "%s" % info["value"][i]

                            if i != len(info['value']) - 1:
                                command += "|"

                        command += '\''

                    command += " %s" % get_location(attributes)

                
                if criterium == "name":
                    command = "ls"
                    command += get_location(attributes)

                    if info["degree"] == "equals":
                        for value in info["value"]:
                            command = command + " | grep %s" % value

            return command

    elif "question" in attributes:
        question = attributes["question"]

        if question == "what" or question == "which":
            pass

def get_location(attributes):
    location = ""
    if "location" in attributes:
        location_info = attributes["location"]
        if "description" in location_info:
            if location_info["description"] == "this":
                location = " ."
        else:
            location = " %s" % location_info["value"]
    return location


def get_direct_object(token):
    for child in token.children:
        if child.dep == symbols.dobj:
            print("the thing to look for is: %s" % child.text)
            print(child.text, child.pos_, child.dep_)
            return child
    return None


if __name__ == "__main__":
    main()
