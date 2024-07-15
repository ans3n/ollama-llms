#Dockerfile, image, container
# Use Python 3.9 Slim Image as Base 
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
# Add test_llms.py into the container
#ADD test_llms.py /app/test_llms.py

# Install Dependencies
RUN pip install ollama scikit-learn openai

RUN chmod +x run_tests.sh

# Run run.sh when the container launches
CMD ["./run_tests.sh"]
