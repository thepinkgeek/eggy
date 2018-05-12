#!/usr/bin/env python

import spacy
import spacy.symbols as symbols
import subprocess
import sys

def start_state(token, attributes):
    pass

def handle_question(token, attributes):
    attributes["question"] = token.text

def handle_command(token, attributes):
    attributes["command"] = token.text

def state_determiner(token, attributes):
    pass

def get_object_to_search(token, attributes):
    attributes["object_of_search"] = token.lemma_
    attributes["object_of_search_value"] = token.text
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

def process_where_question(token, attributes):
    attributes["question"] = token.text

def process_search_criteria_be(token, attributes):
    pass



states = {
            #wh-questions
            start_state: [
                            (lambda token: token.tag_ == "WP", handle_question),
                            (lambda token: token.tag_ == "WDT", handle_question),
                            (lambda token: token.pos_ == "VERB", handle_command),
                            (lambda token: token.text in ['list'], handle_command),
                            (lambda token: token.tag_ == "WRB", process_where_question),
                         ],
            process_where_question: [
                    (lambda token: token.pos_ == "ADP" and token.dep_ == "prep", state_location),
                    (lambda token: token.lemma_ == "be", process_wh_be),
                ],
            handle_question: [ 
                                (lambda token: token.pos_ == "NOUN", get_object_to_search),
                                (lambda token: token.tag_ == "VBZ" and token.lemma_ == "file" , get_object_to_search),
                             ],
            handle_command: [
                                (lambda token: token.pos_ == "NOUN", get_object_to_search),
                                (lambda token: token.pos_ == "DET", state_determiner),
                ],
            state_determiner: [
                (lambda token: token.pos_ == "NOUN", get_object_to_search),
                ],
            get_object_to_search: [
                                    (lambda token: token.lemma_ == "be", process_wh_be),
                                    (lambda token: token.pos_ == "VERB" and token.lemma_ != "be", get_search_criteria),
                                    (lambda token: token.dep_ == "prep", state_location),
                                    (lambda token: token.tag_ == "WP$", process_wh_criteria),
                                    (lambda token: token.tag_ == "WDT", process_wh_det_criteria),
                                    (lambda token: token.tag_ == "JJR", process_adj_criteria),
                                  ],
            get_search_criteria: [
                                    (lambda token: token.dep_ == "prep", state_search_criteria_value),
                                    (lambda token: token.lemma_ == "be", process_search_criteria_be),
                                    (lambda token: True, state_search_criteria_value),
                                    #(lambda token: token.pos_ == "NOUN", state_search_criteria_value),
                                    #(lambda token: token.pos_ == "PROPN", state_search_criteria_value),
                                 ],
            process_search_criteria_be: [
                                    (lambda token: token.dep_ == "nummod", process_size),
                ],
            state_search_criteria_value : [
                                            (lambda token: token.tag_ == "CC", process_conjunction),
                                            (lambda token: token.tag_ == "IN", state_location),
                                            (lambda token: token.tag_ == "IN", state_location),
                                            (lambda token: token.pos_ == "NOUN", process_conjuncted_criteria),
                                        ],
            state_location : [
                              (lambda token: token.pos_ == "NOUN", state_location_value),
                              (lambda token: token.pos_ == "DET", process_location_determiner),
                           ],
            state_location_value : [
                                        (lambda token: token.pos_ == "VERB" and token.lemma_ != "be", get_search_criteria),
                                        (lambda token: token.lemma_ == "be", process_wh_be),
                                        (lambda token: token.tag_ == "WP$", process_wh_criteria),
                                        (lambda token: token.tag_ == "WDT", process_wh_det_criteria),
                                        (lambda token: token.tag_ == "JJR", process_adj_criteria),
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
                        (lambda token: token.pos_ == "NOUN", get_search_criteria),
                ],
            process_wh_det_criteria : [
                    (lambda token: token.lemma_ == "be", process_wh_be),
                    (lambda token: token.pos_ == "VERB" and token.lemma_ != "be", get_search_criteria),
                ],
            process_wh_be: [
                    (lambda token: token.dep_ == "nsubj", get_object_to_search),
                    (lambda token: token.tag_ == "JJR", process_adj_criteria),
                    (lambda token: token.pos_ == "VERB" and token.dep_ == "relcl", get_search_criteria),
                    (lambda token: token.pos_ == "ADP" and token.dep_ == "prep", state_location),
                    (lambda token: token.pos_ == "NOUN" or token.pos_ == "PROPN", get_object_to_search),
                    (lambda token: token.tag_ == "FW", get_object_to_search),
                ],
            process_adj_criteria: [
                    (lambda token: token.dep_ == "prep" and token.pos_ == "ADP", process_degree),
                    (lambda token: token.dep_ == "quantmod" and token.pos_ == "ADP", process_degree)
                ],
            process_degree : [
                    (lambda token: token.dep_ == "nummod", process_size)
                    ],
            process_size: [
                    (lambda token: token.dep_ == "pobj", process_measurement),
                    (lambda token: token.dep_ == "attr", process_measurement)
                    ],
            process_measurement: [
                    ],

         }

def do_analysis(string, nlp):
    attributes = analyze(string, nlp)
    print(attributes)
    command_string = get_command_string(attributes)

    if command_string is not None:
        print("-------------------------------------")
        print("\n\n\n\n\n\n\n")
        print("executing command = %s " % command_string)
        print(subprocess.getoutput(command_string))


def main():
    print("loading nlp stuff")
    nlp = spacy.load('en_core_web_md')
    print("done loading nlp stuff")
    string = ""
    if(len(sys.argv) > 1):
        for arg in sys.argv[1::]:
            string += arg
            string += " "
    else:
        print("entering subsequent text entry mode.")
        string = input("please input a command/query:")

        while string != "quit":
            do_analysis(string, nlp)
            string = input("please input a command/query:")

    #analyze(input("input command here:"), nlp)
    #analyze("show me all files", nlp)
    #attributes = analyze("show all files in this directory named bla", nlp)
    #print(get_command_string(attributes, True))
    #analyze("list all files", nlp)
    #attributes = analyze("show all files containing hi and dada", nlp)
    #print(get_command_string(attributes, True))

    #attributes = analyze("list all files named larger in pycharm", nlp)
    
    #analyze("show all files which are named filename and larger than 3 kilobytes", nlp)
    #analyze("what file in hello contains bla.txt", nlp)
    #analyze("what file in this directory containing bla.txt", nlp)
    #analyze("what files contain bla and foo which are larger than 3 kilobytes", nlp)
    #analyze("what files contain bla", nlp)
    #analyze("which files are larger than 3 kilobytes", nlp)
    #analyze("show files larger than 3 kilobytes", nlp)
    #analyze("show all files in this directory", nlp)
    #analyze("show all files", nlp)
    
def analyze(the_text, nlp):
    print("analyzing text %s = " % the_text)
    text = (the_text)
    doc = nlp(text)
    current_state = start_state
    attributes = {"isComplete" : True}

    for token in doc:
        print("token = %s, lemma = %s, norm = %s, pos = %s, tag = %s, tag_ = %s, dep = %s" % \
                (token.text, token.lemma_, token.norm_, token.pos_, 
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

def process_ack_command(attributes, criteria):
    command = "ack \'"
    info = attributes["criteria"][criteria]
    if info["degree"] == "equals":
        for i in range(0, len(info["value"])):
            command = command + "%s" % info["value"][i]

            if i != len(info['value']) - 1:
                command += "|"

    command += '\''
    command += " %s" % get_location(attributes)
    return command

def process_ls_command(attributes, criteria):
    object_of_search = attributes["object_of_search"]
    print("object_of_search = %s" % object_of_search)
    command = "ls -l"
    command += get_location(attributes)

    command += "| egrep"
    if object_of_search == "file":
        command += " -v"
    elif object_of_search == "directory":
        pass
    else:
        command += " -v"
    command += " \'^d\'"

    if "criteria" in attributes and criteria != "":
        info = attributes["criteria"][criteria]
    
        if info["degree"] == "equals":
            for value in info["value"]:
                command = command + " | grep %s" % value

    return command


def process_find_size_command(attributes, name):
    object_of_search = attributes["object_of_search"]
    command = "find"
    command += get_location(attributes)

    if object_of_search == "file":
        command += " -type f"
    elif object_of_search == "directory":
        command += " -type d"
    else:
        command += " -type f"

    if name == "large":
        command += " -size +"
    elif name == "small":
        command += " -size -"
    else:
        command += " -size +"

    command += process_quantity(attributes["criteria"][name])
    command += "| xargs du -sh"
    return command

def process_find_locate_command(attributes, name):
    command = "find"
    command += get_location(attributes)
    command += " -name "
    command += "\"%s\"" % attributes["object_of_search_value"]
    return command

def process_quantity(criteria):
    value = criteria["value"][0]["value"]
    if "quantity" in criteria["value"][0]:
        quantity = criteria["value"][0]["quantity"].lower()
    else:
        quantity = ""

    if quantity == "bytes":
        return "%sc " % value
    elif quantity == "words":
        return "%sw " % value
    elif quantity == "kilobytes":
        return "%sk " % value
    elif quantity == "megabytes":
        return "%sM " % value
    elif quantity == "gigabytes":
        return "%sG " % value
    else:
        return value


def get_command_string(attributes):
    if not attributes["isComplete"]:
        print("sorry, i can't process your request") 
        return None

    if ("command" in attributes and attributes["command"] in ["show", "give", "list"]) or  \
       ("question" in attributes and attributes["question"] in ["what", "which", "where"]):
            if "question" in attributes and attributes["question"] == "where" and attributes["object_of_search"] != "":
                return process_find_locate_command(attributes, "locate")
            elif "criteria" in attributes:
                if "contain" in attributes["criteria"]:
                    if attributes["object_of_search"] == "directory":
                        print("Sorry, I can't query directories recursively.")
                        return None
                    return process_ack_command(attributes, "contain")
                elif "name" in attributes["criteria"]:
                    return process_ls_command(attributes, "name")
                elif "locate" in attributes["criteria"]:
                    return process_find_locate_command(attributes, "locate")
                elif "large" in attributes["criteria"]:
                    return process_find_size_command(attributes, "large")
                elif "small" in attributes["criteria"]:
                    return process_find_size_command(attributes, "small")
            elif "command" in attributes and attributes["command"] in ["show", "list"]:
                return process_ls_command(attributes, "")
            elif "location" in attributes:
                return process_ls_command(attributes, "")
            else:
                print("sorry, i don't support this yet!")

    else:
        print("sorry, i don't support this yet!")


def get_location(attributes):
    location = ""
    if "location" in attributes:
        location_info = attributes["location"]
        if "description" in location_info:
            if location_info["description"] == "this":
                location = " ."
        else:
            location = " %s" % location_info["value"]
    elif "criteria" in attributes and "locate" in attributes["criteria"]:
        for value in attributes["criteria"]["locate"]["value"]:
            print(value)
            if value != "in":
                location = " %s" % value
    else:
        location = " ."
    return location

if __name__ == "__main__":
    main()
