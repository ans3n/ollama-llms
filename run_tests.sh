#!/bin/bash

# Define the models you want to test
models=("llama2-uncensored" "llama3" "gemma:2b" "gemma:7b" "mistral" "llava" "gpt-3.5-turbo")

# Create the outputs directory if it doesn't exist
if [ ! -d "./outputs" ]; then
    mkdir -p "./outputs"
  fi

# Loop through each model
for model in "${models[@]}"
do
  echo "Starting analysis of $model."
  # Replace colons with underscores for the directory name
  dir_name=$(echo "$model" | tr ':.' '_')
  echo "replaced colons"

  # Create the model-specific directory
  if [ ! -d "./outputs/$dir_name" ]; then
    echo "create model speicifc directory"
    mkdir -p "./outputs/$dir_name"
  fi

  echo "about to run script on $model with directory name $dir_name"
  # Run the Python script and redirect the output. NOTE - CHANGE FROM SMALL FILES TO REGULAR LATER
  python3 test_llms.py --model "$model" --pred_file "./outputs/$dir_name/pred-small.txt" --resp_file "./outputs/$dir_name/rawresp-small.txt" > "./outputs/$dir_name/stdout.txt"

  echo "Analysis of $model complete. Analysis saved to ./outputs/$dir_name."

  #NOTE: REMOVE LATER
  exit 0
done
