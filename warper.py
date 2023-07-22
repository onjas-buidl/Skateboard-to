import os
import git
from git import Repo
import openai

# Define the local directory
repo_URL = "https://github.com/onjas-buidl/GPT_email_generator"

repo_name = repo_URL.split("/")[-1]
base_dir = "/Users/jasonhu/Desktop/"
# Create new folder based on repo_name
local_dir = os.path.join(base_dir, repo_name)
if os.path.exists(local_dir) and os.listdir(local_dir):
    raise Exception("The repository already exists and has content inside. Aborting.")
else:
    os.makedirs(local_dir, exist_ok=True)


Repo.clone_from(repo_URL, local_dir)

# Change the working directory to the local directory
os.chdir(local_dir)
repo = Repo(local_dir)

# Pull the latest codebase from Github
origin = repo.remotes.origin
origin.pull()







def update_file_with_llm(file_path):
    # Load the codebase into a variable
    with open(file_path, 'r') as file:
        codebase = file.read()

    import openai

    openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Python code editor that reformat code, changing from OpenAI API to Langchain API."},
            {"role": "user", "content": "Please read through the following file that is currently using OpenAI API: \n```Python\n{}```"},
        ]
    )

    # Feed the codebase into OpenAI
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=codebase,
      temperature=0.5,
      max_tokens=100
    )

    # Update the codebase with the new code
    with open(file_path, 'w') as file:
        file.write(response.choices[0].text.strip())



# Load all .py files in local_dir separately
for root, dirs, files in os.walk(local_dir):
    # print(root, '===', dirs,'===', files)
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            update_file_with_llm(file_path)



# Commit the changes with a relevant message
repo.git.add(update=True)
repo.index.commit("CodeWarp: Update codebase to Martian API.")

# Push the changes to Github
origin.push()
