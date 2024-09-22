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
NAME_STR = "Prolog Object Specific Rules"
DESCRIP_STR = "Generate Prolog object specific spatial relations using LLMs from a dataset."

prologue = "The given line contains an object and its components."
prompt_template = "Generate Prolog rules defining spatial relationships between the components for the object '{alias}'. " \
                  "The components are [{components}]. " \
                  "Use directly_above(A, B), directly_right(A, B), directly_ahead(A, B), and directly_connected(A, B) as appropriate, where A is relative to B."

followup = "Only include the rules in your answer on each new line"

models = ["llama2-uncensored"]
if INCLUDE_GPT:
    models += ["gpt-3.5-turbo", "gpt-4-turbo"]

# Function to read objects.txt
def load_objects(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    objects = [line.strip().split(', ') for line in lines]
    return objects

# Query LLM to generate Prolog rules
def generate_prolog_rules(model, alias, components, use_cpu, pull_models):
    question = prompt_template.format(alias=alias, components=', '.join(components))
    messages = [{'role': 'user', 'content': question}]
    
    if "gpt" in model:
        response = client.chat.completions.create(model=model, messages=messages)
        response_text = response.choices[0].message.content.strip()
    else:
        if pull_models:
            ollama.pull(model)
        options = {"num_gpu": 0} if use_cpu else {}
        response = ollama.chat(model=model, messages=messages, options=options)
        response_text = response['message']['content'].strip()

    return response_text

def main(args):
    # Load objects from the dataset
    objects = load_objects(args.objects_file)
    
    # Open the output file for writing Prolog rules
    with open(args.output_file, 'w') as f_out:
        for obj in objects:
            alias = obj[0]
            components = obj[1:]
            prolog_rules = generate_prolog_rules(args.model, alias, components, args.cpu, args.pull_models)
            
            # Write the generated rules to the file
            f_out.write(f"Object: {alias}\n")
            f_out.write(prolog_rules + "\n\n")

    print(f"Prolog rules generated and written to {args.output_file}.")

# CLI setup
def config_cli_parser(parser):
    parser.add_argument("--objects_file", default="objects.txt", help="Path to the objects dataset file.")
    parser.add_argument("--output_file", default="object-rules.txt", help="Path to save the generated Prolog rules.")
    parser.add_argument("--model", default="llama2-uncensored", help="LLM model to use.")
    parser.add_argument("--cpu", action="store_true", help="Use CPU instead of GPU.")
    parser.add_argument("--pull_models", action="store_true", help="Force pull models associated with Ollama.")
    return parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=NAME_STR, description=DESCRIP_STR)
    parser = config_cli_parser(parser)
    args = parser.parse_args()
    main(args)
