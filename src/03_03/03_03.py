# import OS, OpenAI, and time modules
import openai
import os
from openai import OpenAI
import time

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def upload_file(path):
    try:
        file = client.files.create(file=open(path, "rb"), purpose="assistants")

        return file.id
    except Exception as e:
        print(e)
        return e


def create_assistant(file_id):
    try:
        assistant = client.beta.assistants.create(
            name="Coding Bot",
            instructions="""Generate a file, always. You are an expert Python developer.
                           When asked a to solve a query, you write and run code to 
                           answer the question. Make the file id available for download.""",
            model="gpt-3.5-turbo",
            tools=[{"type": "code_interpreter"}],
        )

        # Update assistant with file_id
        client.beta.assistants.update(
            assistant_id=assistant.id, file_ids=[file_id]
        )

        return assistant.id
    except openai.APIError as e:
        print(e.http_status)
        print(e.error)
        return e.error


def query_assistant(assistant_id, user_query):
    try:
        thread = client.beta.threads.create(
            messages=[{"role": "user", "content": user_query}]
        )

        return thread.id
    except openai.APIError as e:
        print(e.http_status)
        print(e.error)
        return e.error


def run(assistant_id, thread_id):
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )

        time.sleep(10)

        while True:
            print(f"{run.id=} {run.status=}")

            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )

            status = run.status

            if status == "completed":
                break
            else:
                time.sleep(10)

        print(f"{run.id=} {run.status=}")

        # retrieve the messages
        messages = client.beta.threads.messages.list(thread_id=thread_id)

        return messages

    except openai.APIError as e:
        print(e.http_status)
        print(e.error)
        return e.error

def download_file(messages):     
    try:
        for thread_message in messages.data:
            # Accessing the content array within each ThreadMessage
            for content in thread_message.content:
                # Checking if the content type is 'text'
                if content.type == 'text':
                    # Accessing the annotations within the text content
                    for annotation in content.text.annotations:
                        # Checking for file_path type in annotations
                        if annotation.type == 'file_path':
                            # Extracting the file_id
                            file_id = annotation.file_path.file_id
                            # Extracting the file path
                            file_path = annotation.text

                            # Check if the file path contains '.png'
                            if '.png' in file_path:
                                image_file_id = file_id
                            elif '.py' in file_path:
                                code_file_id = file_id
                                
        
        #get file name
        file_name = client.files.with_raw_response.retrieve_content(image_file_id) 

        #download and save the file locally
        with open("./travel_map.png", "wb") as file:  
            file.write(file_name.content) 
            
        #clean up file
        client.files.delete(image_file_id)
        
    except openai.APIError as e:
        print(e.http_status)
        print(e.error)
        return e.error
    except Exception as e:
        print(e)
        return e

# Function to retrieve the steps of a specific run
def get_code_interpreter_logs(thread_id, run_id):
    try:
        # List the steps for the specified thread and run
        steps = client.beta.threads.runs.steps.list(
          thread_id=thread_id,
          run_id=run_id
        )
        
        #loop and print the messages out
        for step in steps:
            # Check if the step is a tool call and involves the code interpreter
            if step.type == 'tool_calls':
                for tool_call in step.step_details.tool_calls:
                    if tool_call.type == 'code_interpreter':
                        # Print the code input
                        print("\n------Code Input:------\n", tool_call.code_interpreter.input)
                         # Print the code outputs (logs)
                        for output in tool_call.code_interpreter.outputs:
                            if output.type == 'image':
                                print("\n------Code Output Logs:------\n", output)
                            else:
                                print("\n------Code Output Logs:------\n", output.logs)
                        print("==================================\n")    

    except openai.APIError as e:
        print(e.http_status)
        print(e.error)
        return e.error

file_id = upload_file('visits.xlsx')

print(file_id)

assistant_id = create_assistant(file_id)

print(assistant_id)

user_query = '''Plot the given list of cities on the image of a world map using red pins. 
                The plot can be estimates and doesn't need to be 100% accurate. 
                Provide the file id of the image available for download.'''

thread_id = query_assistant(assistant_id, user_query)
print(thread_id)

run_id = run(assistant_id, thread_id)


from IPython.display import Image

image = "./travel_map.png"
print(image)

Image(url=image)
