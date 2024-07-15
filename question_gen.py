import json
import random
import argparse


# Constants.
NAME_STR = "Question Generator"
DESCRIP_STR = ""




#---------------------------------[module code]---------------------------------


question_template = "In a {alias}, with components [{components}], is '{source}' {relationship} '{target}'?"


opposites = {
        "above": "below",
        "below": "above",
        "left of": "right of",
        "right of": "left of",
        "ahead": "behind",
        "behind": "ahead of",
        "connected": "not connected to"
    }

relnames = {
    "above": "above",
    "below": "below",
    "left of": "left of",
    "right of": "right of",
    "ahead": "ahead of",
    "behind": "behind",
    "connected": "connected to"
}



def main(args):
    assert args.n >= 0
    with open(args.obj_json, 'r') as f:
        obj_data = json.load(f)
    dsx, dsy = [], []   # X and y components of the dataset.
    for i in range(args.n):
        obj = random.choice(obj_data)
        alias = random.choice(obj["alias"])
        edge = random.choice(obj["edges"])   # Random choose a relationship.
        source = edge["source"]
        target = edge["target"]
        relationship = edge["relationship"]
        name_relationship = relnames[relationship]
        wrong_relationship = opposites[relationship]
        answer = random.choice([True, False])
        if answer:
            question = question_template.format(alias=alias, components=', '.join(obj["nodes"]), source=source, relationship=name_relationship, target=target)
        else:
            question = question_template.format(alias=alias, components=', '.join(obj["nodes"]), source=source, relationship=wrong_relationship, target=target)
        dsx.append(question)
        dsy.append(answer)
    with open(f'{args.out_dir}/dsx.txt', 'w') as f:
        for question in dsx:
            f.write(question + '\n')
    with open(f'{args.out_dir}/dsy.txt', 'w') as f:
        for answer in dsy:
            f.write(str(answer) + '\n')
    print("Done.")







def config_cli_parser(parser):
    parser.add_argument('--n', type=int, default=100, help='Number of questions to generate. Must be a positive integer.')
    parser.add_argument('--obj_json', type=str, default='./obj_data.json', help='Path to the input JSON file.')
    parser.add_argument('--out_dir', type=str, default='./', help='Directory where output files will be saved. Defaults to the current directory.')
    return parser



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog = NAME_STR, description = DESCRIP_STR)   # Create module's cli parser.
    parser = config_cli_parser(parser)
    args = parser.parse_args()
    main(args)

#===============================================================================
