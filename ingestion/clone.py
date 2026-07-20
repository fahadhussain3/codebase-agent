import os
from git import Repo
import config

def clone_repo(repo_url):
    """
    Clones a GitHub repo into the local storage folder.
    Returns the local path where it was cloned.
    """
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    local_path = os.path.join(config.REPO_CLONE_PATH, repo_name)

    if os.path.exists(local_path):
        print(f"Repo already cloned at {local_path}, skipping clone.")
        return local_path

    os.makedirs(config.REPO_CLONE_PATH, exist_ok=True)
    print(f"Cloning {repo_url} into {local_path} ...")
    Repo.clone_from(repo_url, local_path)
    print("Clone complete.")
    return local_path