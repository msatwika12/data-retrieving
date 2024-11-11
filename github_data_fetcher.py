import requests
import json

# GitHub personal access token (replace with your token)
GITHUB_ACCESS_TOKEN = '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'

# Define headers with authentication token
headers = {
    'Authorization': f'token {GITHUB_ACCESS_TOKEN}'
}

def extract_repo_owner_and_name(repo_url):
    """
    Extract the repository owner and name from the GitHub URL.
    """
    repo_url = repo_url.rstrip("/")
    parts = repo_url.split("/")
    repo_owner = parts[-2]
    repo_name = parts[-1]
    return repo_owner, repo_name

def fetch_github_repo_data(repo_url):
    """
    Fetch data from GitHub repository including issues, pull requests, and source code comments.
    """
    # Extract repo owner and name from the URL
    repo_owner, repo_name = extract_repo_owner_and_name(repo_url)

    # Fetch issues and comments
    issue_data = fetch_issues_and_comments(repo_owner, repo_name)

    # Fetch pull requests and comments
    pr_data = fetch_pull_requests_and_comments(repo_owner, repo_name)

    # Fetch source code and comments
    source_code_data = fetch_source_code_and_comments(repo_owner, repo_name)

    # Combine all data into a single dictionary
    all_data = {
        "issues": issue_data,
        "pull_requests": pr_data,
        "source_code": source_code_data
    }

    # Save data to a JSON file
    with open("complete_repository_data.json", "w") as json_file:
        json.dump(all_data, json_file, indent=4)

def fetch_issues_and_comments(repo_owner, repo_name):
    """
    Fetch issues and comments from the GitHub repository.
    """
    issues_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    response = requests.get(issues_url, headers=headers)

    print("Response status code:", response.status_code)  # Debugging line
    print("Response content:", response.content)  # Debugging line

    if response.status_code == 200:
        issue_data = []
        issues = response.json()

        for issue in issues:
            issue_info = {
                'title': issue['title'],
                'description': issue['body'],
                'comments': []
            }

            # Fetch comments for each issue
            comments_url = issue['comments_url']
            comments_response = requests.get(comments_url, headers=headers)

            if comments_response.status_code == 200:
                comments = comments_response.json()
                for comment in comments:
                    issue_info['comments'].append({
                        'user': comment['user']['login'],
                        'comment': comment['body']
                    })

            issue_data.append(issue_info)

        return issue_data
    else:
        print(f"Error fetching issues: {response.status_code}")
        return []

def fetch_pull_requests_and_comments(repo_owner, repo_name):
    """
    Fetch pull requests and comments from the GitHub repository.
    """
    prs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    response = requests.get(prs_url, headers=headers)

    print("Response status code:", response.status_code)  # Debugging line
    print("Response content:", response.content)  # Debugging line

    if response.status_code == 200:
        pr_data = []
        prs = response.json()

        for pr in prs:
            pr_info = {
                'title': pr['title'],
                'description': pr['body'],
                'comments': [],
                'owner': pr['user']['login']
            }

            # Fetch comments for each pull request
            comments_url = pr['comments_url']
            comments_response = requests.get(comments_url, headers=headers)

            if comments_response.status_code == 200:
                comments = comments_response.json()
                for comment in comments:
                    pr_info['comments'].append({
                        'user': comment['user']['login'],
                        'comment': comment['body']
                    })

            pr_data.append(pr_info)

        return pr_data
    else:
        print(f"Error fetching pull requests: {response.status_code}")
        return []

def fetch_source_code_and_comments(repo_owner, repo_name):
    """
    Fetch source code and comments from the GitHub repository.
    """
    code_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    response = requests.get(code_url, headers=headers)

    print("Response status code:", response.status_code)  # Debugging line
    print("Response content:", response.content)  # Debugging line

    if response.status_code == 200:
        source_code_data = []
        files = response.json()

        for file in files:
            if file['type'] == 'file':
                file_data = {
                    'file_name': file['name'],
                    'comments': []
                }
                file_url = file['download_url']

                # Fetch file content
                content = get_file_content(file_url, file['name'])
                file_data['comments'] = content  # Adding file comments to the data

                source_code_data.append(file_data)

        return source_code_data
    else:
        print(f"Error fetching source code: {response.status_code}")
        return []

def get_file_content(file_url, file_name):
    """
    Fetch content of the file.
    """
    response = requests.get(file_url, headers=headers)
    print(f"Processing file: {file_name}")  # Debugging line

    if response.status_code == 200:
        try:
            return response.text.split("\n")  # Split content by line for simplicity
        except Exception as e:
            print(f"Error decoding JSON or missing 'content' field in {file_url}: {str(e)}")
            return []
    else:
        print(f"Error fetching content for {file_name}: {response.status_code}")
        return []

if __name__ == "__main__":
    # Example GitHub repository URL (replace with your repository)
    repo_url = "https://github.com/opensearch-project/opensearch-spark"  # Change this to your repo URL
    fetch_github_repo_data(repo_url)
