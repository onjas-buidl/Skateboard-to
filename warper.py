import os
import git
import re
from git import Repo
import openai

# Define the local directory
repo_URL = "https://github.com/onjas-buidl/GPT_email_generator"
base_dir = os.getcwd()



repo_name = repo_URL.split("/")[-1]
# Create new folder based on repo_name
target_repo_dir = os.path.join(base_dir, repo_name)
if os.path.exists(target_repo_dir) and os.listdir(target_repo_dir):
    print('This repo already exists and we delete it for demo purpose.')
    import shutil
    shutil.rmtree(target_repo_dir)
else:
    os.makedirs(target_repo_dir, exist_ok=True)

Repo.clone_from(repo_URL, target_repo_dir)
print('Cloned the repo successfully. {} is created.'.format(target_repo_dir))
# Change the working directory to the local directory
os.chdir(target_repo_dir)
repo = Repo(target_repo_dir)

# Pull the latest codebase from GitHub
origin = repo.remotes.origin
origin.pull()

os.chdir(base_dir)
#
# # Read sample_prompt_file.txt as string
# with open('sample_prompt_file.txt', 'r') as file:
#     sample_prompt = file.read()


def extract_code_segments(text):
    code_segments = re.findall(r"```(?:Python|python)?\s*([\s\S]*?)```", text)
    if len(code_segments) == 0:
        raise Exception("No code segments found in the text.")
    return code_segments

def detect_openai_api(code_segment):
    if "openai" in code_segment.lower():
        return True
    else:
        return False

def update_file_with_llm(file_path):
    """

    :param file_path:
    :return -> bool: whether the file is updated.
    """
    # Load the codebase into a variable
    with open(file_path, 'r') as file:
        codebase = file.read()

    if not detect_openai_api(codebase):
        return False

    respnose = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Python code editor that reformat code, changing from OpenAI API to Langchain API."},
            {'role': 'user', "content": """This is usually how to call OpenAI API

```python
import openai

response = openai.ChatCompletion.create(
  model="gpt-4", # alternatively, you can use `model = 'gpt-3.5-turbo'`
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
)

print(response['choices'][0]['message']['content'])
# print result: The 2020 World Series was played at the Globe Life Field in Arlington, Texas.
```

This is an example of calling chat models with OpenAI API in LangChain, performing the same utility. 

```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# alternatively, you can use model_name = 'gpt-3.5-turbo'
llm = ChatOpenAI(model_name='gpt-4')

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Who won the world series in 2020?"),
		AIMessage(content="The Los Angeles Dodgers won the World Series in 2020."),
		HumanMessage(content="Where was it played?")
]
response = llm(messages)

# response: AIMessage(content='The 2020 World Series was played at Globe Life Field in Arlington, Texas.', additional_kwargs={}, example=False)
# to print the result, use `print(response.content)`
```

Both code snippets assume that there is an OPENAI_API_KEY environmental variable. If the key is set in other ways, make sure to set `os.environ["OPENAI_API_KEY"] = "whatever key format the codebase is using"`"""},
            {"role": "assistant", "content": "Understand, I will reformat a file from OpenAI API to LangChain. Please send me the file content to reformat."},
            {"role": "user", "content": """In the following code, please find usage of the OpenAI API, and replace it with LangChain API. Do not change anything else. 
\n```Python\n{code}\n```\nPlease output the complete file of the reformatted code and nothing else.""".format(code=codebase)},
        ]
    )

    output = respnose['choices'][0]['message']['content']

    cleaned_file_content = extract_code_segments(output)[0]

    # Update the codebase with the new code
    with open(file_path, 'w') as file:
        file.write(cleaned_file_content)

    return True


# Load all .py files in local_dir separately
for root, dirs, files in os.walk(target_repo_dir):
    # print(root, '===', dirs,'===', files)
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            is_updated = update_file_with_llm(file_path)
            if is_updated:
                print("Updated file: {}".format(file_path))


# Commit the changes with a relevant message
repo.git.add(update=True)
repo.index.commit("CodeWarp: Update codebase to LangChain.")

# Push the changes to Github
origin.push()