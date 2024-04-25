#import OS, OpenAI, and time modules
import openai
import os
from openai import OpenAI
import time

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY']  
)

def upload_file(path):
    try:
        file = client.files.create(
            file=open(path, "rb"),
            purpose='assistants'
        )
        
        return file.id
    except Exception as e:
        print(e)
        return e
    
def create_assistant(file_id):
    try:
        assistant = client.beta.assistants.create(
            name="Coding Bot",
            instructions='''Generate a file, always. You are an expert Python developer.
                           When asked a to solve a query, you write and run code to 
                           answer the question. Make the file id available for download.''',
            model="gpt-3.5-turbo",
            tools=[{"type": "code_interpreter"}]
        )
        
        # Update assistant with file_id
        client.beta.assistants.update(
            assistant_id=assistant.id,
            file_ids=[file_id]
        )

        return assistant.id
    except openai.APIError as e:
        print(e.http_status)
        print(e.error)
        return e.error

    
def query_assistant(assistant_id, user_query):
    try:
        thread = client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": user_query
                }
            ]
        )
        
        return thread.id
    except openai.APIError as e:
        print(e.http_status)
        print(e.error)
        return e.error
    
def run(assistant_id, thread_id):
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        time.sleep(10)
        
        while True:
            print(f'{run.id=} {run.status=}')

            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            status = run.status

            if status == 'completed':
                break
            else:
                time.sleep(10) 

        print(f'{run.id=} {run.status=}')
        
        #retrieve the messages 
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )

   
        return messages
        
    except openai.APIError as e:
        print(e.http_status)
        print(e.error)
        return e.error
    
file_id = upload_file('./src/Formatted_Customer_Feedback_Product_Ratings.csv')

print(file_id)

assistant_id = create_assistant(file_id)