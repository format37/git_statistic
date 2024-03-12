import pandas as pd
import pytz
import requests
from github import Github
import re
import json


def list_python_files(repo, path=""):
    files_list = []
    contents = repo.get_contents(path)

    for file_content in contents:
        if file_content.type == "dir":
            files_list.extend(list_python_files(repo, file_content.path))
        elif (
            file_content.name.endswith(".py")
            or file_content.name.endswith(".ipynb")
            or file_content.name == "requirements.txt"
        ):
            files_list.append(file_content)
    return files_list


def get_file_creation_date(repo, file_path):
    commits = repo.get_commits(path=file_path)
    if commits.totalCount > 0:
        first_commit = commits.get_page(-1)[-1]  # Getting the last page and the last commit
        creation_date = first_commit.commit.author.date
        return creation_date.astimezone(pytz.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    return None


def extract_imports(file_content, filename):
    if filename == "requirements.txt":
        requirements_regex = r"^([\w\-_]+)(\[.*\])?(==[\w\.\-]+)?"
        requirements = re.findall(requirements_regex, file_content, re.MULTILINE)
        return ["import " + match[0] for match in requirements]
    else:
        import_regex = r"^import\s+[\w\.]+"
        from_import_regex = r"^from\s+[\w\.]+\s+import\s+[\w\.\*]+"
        imports = re.findall(import_regex, file_content, re.MULTILINE)
        from_imports = re.findall(from_import_regex, file_content, re.MULTILINE)
        return imports + from_imports


def get_repo_data(username, token):
    data = []
    g = Github(token)
    for repo in g.get_user(username).get_repos():
        try:
            files = list_python_files(repo)
            for file in files:
                response = requests.get(file.download_url)
                if file.name.endswith(".py") or file.name == "requirements.txt":
                    file_content = response.text
                elif file.name.endswith(".ipynb"):
                    notebook_json = json.loads(response.text)
                    file_content = "\n".join(
                        "\n".join(cell["source"])
                        for cell in notebook_json["cells"]
                        if cell["cell_type"] == "code"
                    )
                imports = extract_imports(file_content, file.name)
                creation_date = get_file_creation_date(repo, file.path)
                data.append(
                    [repo.name, file.name, creation_date, file.last_modified, imports]
                )
        except Exception as e:
            print(f"Error processing {repo.name}: {e}")
            continue
    return data


def extract_library_name(import_statement):
    if import_statement.startswith("import"):
        return import_statement.split()[1].split(".")[0]
    elif import_statement.startswith("from"):
        return import_statement.split()[1]
    return None


def transform_data(data):
    transformed_data = []

    for item in data:
        repo, filename, first_commit_date, last_update_date, imports = item

        for import_statement in imports:
            library_name = extract_library_name(import_statement)
            if library_name:
                transformed_data.append([repo, filename, first_commit_date, last_update_date, library_name])

    return transformed_data

def simplify_library_name(name):
    return name.split('.')[0]

def main():
    # Authentication
    username = input("Enter your Github username: ")
    token = input("Enter your Github token: ")
    data = get_repo_data(username, token)
    data_temp = transform_data(data)
    df = pd.DataFrame(data_temp)
    df.columns = ['project', 'file', 'date_start', 'date_end', 'library']
    # Convert 'date' column to datetime
    df['date_start'] = pd.to_datetime(df['date_start'], format='%a, %d %b %Y %H:%M:%S GMT')
    df['date_end'] = pd.to_datetime(df['date_end'], format='%a, %d %b %Y %H:%M:%S GMT')
    df['library'] = df['library'].apply(simplify_library_name)
    df.to_csv('git.csv')
    libraries = df['library'].unique()
    cat = {}
    for i, library in enumerate(libraries):
        cat[library] = ''
    # Save cat as json
    with open('cat.json', 'w') as f:
        json.dump(cat, f, indent=1)
    print('Now you may to fill categories in file cat.json')
    print('After that run file report.py')

if __name__ == '__main__':
    main()
