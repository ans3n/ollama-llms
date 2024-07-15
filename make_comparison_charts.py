# Imports.
import argparse
import os
import matplotlib.pyplot as plt

# Constants.
NAME_STR = "LLM Comparison"
DESCRIP_STR = "Script to compare accuracy and average time of different LLM models."

#---------------------------------[module code]---------------------------------

def main(args):
    models = []
    accuracies = []
    avg_times = []
    for model_dir in os.listdir(args.root):
        model_path = os.path.join(args.root, model_dir)
        if os.path.isdir(model_path):
            stdout_file = os.path.join(model_path, 'stdout.txt')
            if os.path.isfile(stdout_file):
                with open(stdout_file, 'r') as f:
                    lines = f.readlines()
                    model_name = lines[0].split(": ")[1].strip()
                    accuracy = float(lines[3].split(": ")[1].strip()[:-1])
                    avg_time = float(lines[4].split(": ")[1].strip().split()[0])
                    models.append(model_name)
                    accuracies.append(accuracy)
                    avg_times.append(avg_time)
    plt.figure(figsize=(10, 5))
    plt.bar(models, accuracies, color='blue')
    plt.xlabel('Models')
    plt.ylabel('Accuracy')
    plt.title('Accuracy of Different LLM Models')
    plt.savefig('accu_barchart.png')
    plt.close()
    plt.figure(figsize=(10, 5))
    plt.bar(models, avg_times, color='green')
    plt.xlabel('Models')
    plt.ylabel('Average Time (seconds)')
    plt.title('Average Time per Question of Different LLM Models')
    plt.savefig('time_barchart.png')
    plt.close()


#--------------------------------[module setup]---------------------------------

def config_cli_parser(parser):
    parser.add_argument("--root", default="./outputs/", help="Root directory containing model outputs.")
    return parser


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog = NAME_STR, description = DESCRIP_STR)
    parser = config_cli_parser(parser)
    args = parser.parse_args()
    main(args)

#===============================================================================
