import os, sys
import argparse
import time

import ollama
from sklearn.metrics import accuracy_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

INCLUDE_GPT = True
if INCLUDE_GPT:
    from openai import OpenAI
    api_key = 'sk-proj-7ZDUngUELm21Pr85tkL5T3BlbkFJtgMpqNHqiXo3XnpyxjSp'
    client = OpenAI(api_key=api_key)

# Constants.
NAME_STR = "LLM Tester"
DESCRIP_STR = "Test LLMs using provided dataset files."

models = ["llama3", "gemma:2b", "gemma:7b", "mistral", "llama2-uncensored", "llava"]
if INCLUDE_GPT:
    models += ["gpt-3.5-turbo", "gpt-4-turbo"]

prologue = "I will ask you a question about simple common objects. Please include 'true' or 'false' in your answer, and explain your chain of logic for why it is true or false."
followup = "Given your answer, summarize with only true or false. Only answer with 'true' or 'false'."

#dictionary to store categories of past responses and questions
memory_history = {}

#---------------------------------[module code]---------------------------------

'''
    Load the binary QA dataset.
'''
def load_dataset(dsx_path, dsy_path):
    with open(dsx_path, 'r') as f:
        questions = f.readlines()
    with open(dsy_path, 'r') as f:
        answers = f.readlines()
    questions = [q.strip() for q in questions]
    answers = [a.strip().lower() == 'true' for a in answers]
    return questions, answers



'''
    Ask a single true or false question to any Ollama LLM.
    Returns 1 for true, 2 for false, and 3 for bad format.
'''
def query_llm(model, question, use_cpu, pull_models):
    messages = []
    question = prologue + question
    messages.append({'role': 'user', 'content': question})
    if "gpt" in model:
        response = client.chat.completions.create(model=model, messages=messages)
        explanation_response = response.choices[0].message.content.strip()
        messages.append({'role': 'assistant', 'content': explanation_response})
        messages.append({'role': 'user', 'content': followup})
        response = client.chat.completions.create(model=model, messages=messages)
        response_text = response.choices[0].message.content.strip().lower()
    else:
        if pull_models:
            ollama.pull(model)
        options = {"num_gpu": 0} if use_cpu else {}
        response = ollama.chat(model=model, messages=messages, options=options)
        explanation_response = response['message']['content'].strip()
        messages.append({'role': 'assistant', 'content': explanation_response})
        messages.append({'role': 'user', 'content': followup})
        response = ollama.chat(model=model, messages=messages, options=options)
        response_text = response['message']['content'].strip().lower()
    has_true = 'true' in response_text
    has_false = 'false' in response_text
    response_tup = (explanation_response, response_text)
    if has_true and not has_false:
        return (1, response_tup)
    elif has_false and not has_true:
        return (2, response_tup)
    else:
        return (3, response_tup)

def extractCategory(question):
    return question.split()[2]  # extracts the 3rd word from the sentence - "In a xyz"

def cosineSimilarityTest(question, category):
    if category in memory_history:
        # Vectorize the question
        vectorizer = TfidfVectorizer().fit_transform([q for q, _ in memory_history[category]])
        vectorized_question = vectorizer.transform([question])
        similarities = cosine_similarity(vectorized_question, vectorizer).flatten()

        # Find the question most similar to
        biggest_index = similarities.argmax()
        most_similar = similarities[biggest_index]

        # Similarity threshold - adjust as necessary
        similarity_threshold = 0.75
        if most_similar >= similarity_threshold:
            return memory_history[category][biggest_index]
    
    # returns none if category not in memory history or most similar question is below the defined similarity threshold
    return None, None


def main(args):
    #print("enter test llms main \n")
    questions, true_answers = load_dataset(args.dsx, args.dsy)  #dsx contains questions and dsy their respective answers
    predicted_answers = []      # Used to count all answers as str.
    valid_answers = []          # Used to count only answers that are well-formed as bool.
    responses = []              # Used to hold raw str responses.
    total_time = 0
    wrong_format_count = 0

    total_runs = 5

    for i in range(total_runs):
        #print("before for loop\n")
        #for every question do the following:
        for question in questions:
            #print("examinign question " + question)
            start_time = time.time()

            """ category = extractCategory(question)
            previous_similarQuestion, previous_similarResponse = cosineSimilarityTest(question, category)
            if previous_similarQuestion and previous_similarResponse:
                print("found similar enough question before\n")
            if category in memory_history:
                category_history = memory_history[category]    #dictionary of previous responses for that category

                #Use previous responses to adjust the question or decision-making process
                found = False
                for prev_question, prev_response in category_history:
                    if prev_question == question:
                        found = True
                        result, full_response = prev_response
                        break
                if found:
                    print(f"Found previous response for '{question}': {full_response}") """

            #print("start time is " + str(start_time))
            # get the result(true/false/bad format) from llama as well as explanation
            result, full_response = query_llm(args.model, question, args.cpu, args.pull_models) 
            #print("\nresult and responses done\n")

            responses.append(full_response)
            end_time = time.time()
            total_time += (end_time - start_time)

            # if new category, create a new dictionary within response history for it
            """ if category not in memory_history:
                memory_history[category] = []
            memory_history[category].append((question, full_response)) """

            #print("\nresponses are" + str(responses))
            #if llama thought the question was true
            if result == 1:
                #print("respones are found as true\n")
                prediction = True
                valid_answers.append(prediction)
                predicted_answers.append("true")
            #if llama thought the question was false
            elif result == 2:
                #print("respones are found as false\n")
                prediction = False
                valid_answers.append(prediction)
                predicted_answers.append("false")
            #if llama thought the question was badly formatted
            else:
                #print("respones are found as bad format\n")
                wrong_format_count += 1
                valid_answers.append(None)
                predicted_answers.append("bad-format")
        
        #print("about to create valid true answers\n")
        # run through every answer and create a tuple of actual vs. predicted answer given that the answer was in a good format
        valid_true_answers = [a for a, p in zip(true_answers, valid_answers) if p is not None]
        #print("valid true answers" + str(valid_true_answers))

        #print("\nabout to create valid predicted answers\n")
        # take only the answers that were in good formats
        valid_predicted_answers = [p for p in valid_answers if p is not None]
        #print("valid predicted answers: " + str(valid_predicted_answers) + "\n")

        # accuracy metrics
        accuracy = accuracy_score(valid_true_answers, valid_predicted_answers)
        avg_time_per_question = total_time / len(questions)
        wrong_format_percent = (wrong_format_count / len(questions)) * 100
        #print("accuracy: " + accuracy + " average time: " + avg_time_per_question + "wrong format percent " + wrong_format_percent + "\n")
        # if the prediction file exists, write every answer the chatbot predicted
        if args.pred_file:
            #print("write to prediction file\n")
            with open(args.pred_file, 'w') as f:
                for answer in predicted_answers:
                    f.write(f"{answer}\n")

        # if the response file exsits write every explanation the chatbot gave to every question
        if args.resp_file:
            #print("write to response file\n")
            with open(args.resp_file, 'w') as f:
                for r in responses:
                    f.write(f"{str(r)}\n")

    print(f"Model: {args.model}.")
    print(f"CPU only: {args.cpu}.")
    print(f"DS size: {len(questions)}.")
    print(f"Accuracy: {accuracy:.2f}.")
    print(f"Average time per question: {avg_time_per_question:.2f} seconds.")
    print(f"Wrong format responses: {wrong_format_count} ({wrong_format_percent:.2f}%).")






#--------------------------------[module setup]---------------------------------

def config_cli_parser(parser):
    #TODO: CHANGE LATER - CHANGE BACK TO ORIGINAL FILES LATER
    parser.add_argument("--dsx", default="./dsx-small.txt", help="Path to the questions dataset file.")
    parser.add_argument("--dsy", default="./dsy-small.txt", help="Path to the answers dataset file.")
    parser.add_argument("--model", default="llama3", help="LLM model to use.")
    parser.add_argument("--cpu", action="store_true", help="Use CPU instead of GPU.")
    parser.add_argument("--pull_models", action="store_true", help="Force pull models associated with Ollama.")
    parser.add_argument("--pred_file", help="Path to save the predicted responses.")
    parser.add_argument("--resp_file", help="Path to save raw response strings.")
    return parser

#enters with inputs of model, prediction file, response file
if __name__ == '__main__':
    #print("entered test_llms\n")
    parser = argparse.ArgumentParser(prog=NAME_STR, description=DESCRIP_STR)
    print("parsed argument as " + str(parser))
    #print("parsed argument as " + parser)

    parser = config_cli_parser(parser)      #adds additional command line arguments
    #print("\nadded additional arguments to parser, now as " + parser)
    print("\nadded additional arguments to parser, now as " + str(parser))

    args = parser.parse_args()
    print("\n arguments are " + str(args))

    #prints model metrics and write to the prediction file what the chatbot predicted and to the response file its explanation
    main(args)

#===============================================================================
