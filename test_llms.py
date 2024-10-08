import os, sys
import argparse
import time

import ollama
from sklearn.metrics import accuracy_score
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



def main(args):
    questions, true_answers = load_dataset(args.dsx, args.dsy)
    predicted_answers = []      # Used to count all answers as str.
    valid_answers = []          # Used to count only answers that are well-formed as bool.
    responses = []              # Used to hold raw str responses.
    total_time = 0
    wrong_format_count = 0

    for question in questions:
        start_time = time.time()
        result, full_response = query_llm(args.model, question, args.cpu, args.pull_models)
        responses.append(full_response)
        end_time = time.time()
        total_time += (end_time - start_time)
        if result == 1:
            prediction = True
            valid_answers.append(prediction)
            predicted_answers.append("true")
        elif result == 2:
            prediction = False
            valid_answers.append(prediction)
            predicted_answers.append("false")
        else:
            wrong_format_count += 1
            valid_answers.append(None)
            predicted_answers.append("bad-format")
    valid_true_answers = [a for a, p in zip(true_answers, valid_answers) if p is not None]
    valid_predicted_answers = [p for p in valid_answers if p is not None]
    accuracy = accuracy_score(valid_true_answers, valid_predicted_answers)
    avg_time_per_question = total_time / len(questions)
    wrong_format_percent = (wrong_format_count / len(questions)) * 100
    if args.pred_file:
        with open(args.pred_file, 'w') as f:        #TODO: change later back to write
            for answer in predicted_answers:
                f.write(f"{answer}\n")
    if args.resp_file:
        with open(args.resp_file, 'w') as f:        #TODO: change later back to write
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
    parser.add_argument("--dsx", default="./dsx-small.txt", help="Path to the questions dataset file.")
    parser.add_argument("--dsy", default="./dsy-small.txt", help="Path to the answers dataset file.")
    parser.add_argument("--model", default="llama3", help="LLM model to use.")
    parser.add_argument("--cpu", action="store_true", help="Use CPU instead of GPU.")
    parser.add_argument("--pull_models", action="store_true", help="Force pull models associated with Ollama.")
    parser.add_argument("--pred_file", help="Path to save the predicted responses.")
    parser.add_argument("--resp_file", help="Path to save raw response strings.")
    return parser

if __name__ == '__main__':
    run_repeats = 10

    for _ in range(run_repeats):
        parser = argparse.ArgumentParser(prog=NAME_STR, description=DESCRIP_STR)
        parser = config_cli_parser(parser)
        args = parser.parse_args()
        main(args)

#===============================================================================
