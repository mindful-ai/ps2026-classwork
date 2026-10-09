# Push Code to Bitbucket Using an HTTP Access Token

This guide starts from the initial Git configuration on a Windows computer and covers creating a Bitbucket repository, configuring Git, authenticating with an HTTP access token, and pushing your local project.

It uses **Git over HTTPS** with an HTTP access token instead of a Bitbucket password or SSH key.

> **Scope:** These instructions are for Bitbucket Cloud (`bitbucket.org`). Bitbucket Data Center uses a different procedure for some token types.

## Step 1: Install and configure Git

### 1.1 Verify Git installation

Open PowerShell or the VS Code terminal and run:

```powershell
git --version
```

If Git is not installed, download it from the official website:

https://git-scm.com/downloads

### 1.2 Configure your identity

Set your name and email address. These values identify you as the author of Git commits.

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Verify the configuration:

```powershell
git config --global --list
```

Expected output will include:

```text
user.name=Your Name
user.email=you@example.com
```

These are commit-author details, not your authentication credentials.

## Step 2: Create an HTTP access token in Bitbucket

Sign in to Bitbucket:

https://bitbucket.org/

Atlassian offers different token types, and the exact menu depends on whether you are using a personal account or a workspace. Create a token that supports repository access over HTTPS.

For a **workspace access token**, if your workspace and plan support it:

1. Open your Bitbucket workspace.
2. Navigate to **Workspace settings**.
3. Find **Access tokens**.
4. Select the option to create a token.
5. Give it a descriptive name, such as `git-push-token`.
6. Set an expiry date.
7. Grant only the permissions required for your task.

For pushing code, the token needs repository write permission. Read permission is also useful for cloning and fetching. Workspace-level permissions and personal-account token permissions may be named differently.

Official documentation: https://support.atlassian.com/bitbucket-cloud/docs/using-access-tokens/

**Important:** Copy the token when it is displayed and store it securely. Do not paste it into source code, commit it to Git, or share it in a terminal screenshot.

## Step 3: Create a repository in Bitbucket

If you do not already have a remote repository:

1. In Bitbucket, select **Create → Repository**.
2. Select the appropriate workspace and project.
3. Enter a repository name, for example `ai-proj`.
4. Choose the repository's access level.
5. For an existing local project, create the repository **without a README or initial commit** to avoid an unnecessary first-commit history conflict.
6. Click **Create repository**.

Copy the HTTPS repository URL. It will look similar to:

```text
https://bitbucket.org/<workspace-id>/ai-proj.git
```

Replace `<workspace-id>` with your actual Bitbucket workspace ID.

## Step 4: Prepare your local project

Open a terminal in your project directory. For example:

```powershell
cd C:\mindful-ai\ai-proj
```

Check whether Git is already initialized:

```powershell
git status
```

If you see `fatal: not a git repository`, initialize Git:

```powershell
git init
```

Create a `.gitignore` file before staging files. For a Python project, a reasonable starting point is:

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
.env
*.log
.pytest_cache/
.ipynb_checkpoints/
```

Add other project-specific exclusions as needed. Never commit API keys, passwords, access tokens, or private environment files.

Stage and commit your project:

```powershell
git add .
git status
git commit -m "Initial commit"
```

If you have already committed your project, skip the initial commit and continue.

Set the branch name to `main`:

```powershell
git branch -M main
```

## Step 5: Configure the Bitbucket HTTPS remote

Connect your local repository to the Bitbucket repository you created.

```powershell
git remote add origin https://x-token-auth@bitbucket.org/<workspace-id>/ai-proj.git
```

If an `origin` remote already exists, update it instead:

```powershell
git remote set-url origin https://x-token-auth@bitbucket.org/<workspace-id>/ai-proj.git
```

Verify the configuration:

```powershell
git remote -v
```

Expected output:

```text
origin  https://x-token-auth@bitbucket.org/<workspace-id>/ai-proj.git (fetch)
origin  https://x-token-auth@bitbucket.org/<workspace-id>/ai-proj.git (push)
```

Here, `x-token-auth` is the special username used for Bitbucket Cloud repository and workspace access tokens. You will enter the actual token separately when Git prompts for a password. This avoids placing the secret directly in the remote URL.

> **Token-type note:** Bitbucket Cloud has several token types and authentication conventions. Follow the instructions for the exact token you created. If your token's documentation specifies a different username or authentication format, use that format instead.

## Step 6: Push your code using the HTTP access token

Run:

```powershell
git push -u origin main
```

If Git prompts for credentials, use the following:

| Prompt | Value |
|---|---|
| Username | `x-token-auth` (if requested and appropriate for your token type) |
| Password | Paste your HTTP access token |

Depending on the Git credential manager and terminal, you might see only a password prompt because the username is already embedded in the remote URL.

**Do not type the token into the command itself.** Paste it into the password prompt. Password input is normally not displayed on screen.

On a successful push, Git uploads your committed files and sets `origin/main` as the upstream tracking branch.

For subsequent pushes, use:

```powershell
git add .
git commit -m "Describe your changes"
git push
```

## Step 7: Verify the push

Run:

```powershell
git status
git log --oneline -5
git branch -vv
```

Then open your Bitbucket repository in the browser and confirm that your files are visible under the `main` branch.

## Step 8: Common errors and fixes

| Error | Likely cause | Fix |
|---|---|---|
| `Authentication failed` | Invalid, expired, or incorrectly supplied token | Create a valid token and retry |
| `403 Forbidden` | Token lacks write permission | Grant repository write permission |
| `Repository not found` | Incorrect workspace or repository URL, or insufficient access | Verify the HTTPS URL and repository permissions |
| `src refspec main does not match any` | No commit exists on `main` | Stage files, commit, and check `git branch` |
| `remote origin already exists` | Remote already configured | Use `git remote set-url origin ...` |
| `rejected (fetch first)` | Remote contains commits absent locally | Fetch and integrate the remote history before pushing |

If Git keeps using old credentials on Windows:

1. Open **Control Panel → Credential Manager → Windows Credentials**.
2. Locate the relevant Bitbucket credential.
3. Remove the stale entry.
4. Retry the push and authenticate with the correct token.

## Step 9: Security and token details

- Grant only the permissions required for your task. Git operations generally require repository read access for fetching/cloning and repository write access for pushing, but exact permission names depend on the token type.
- Never store a token permanently in a Git remote URL or commit it to a repository.
- If you use a repository or workspace access token, follow Atlassian's token-specific instructions for any required bot username or email.
- If the token expires or is revoked, create a replacement and update your authentication credentials.

Official reference for Bitbucket Cloud:

https://support.atlassian.com/bitbucket-cloud/docs/using-access-tokens/

For a self-hosted **Bitbucket Data Center** server, consult the documentation for your server version. Personal access tokens and project/repository access tokens can have different authentication requirements:

https://confluence.atlassian.com/bitbucketserver/personal-access-tokens-939515499.html

---

## Quick command reference

Run these commands from your project directory, replacing the sample values with your own:

```powershell
# 1. Configure Git identity (usually done once per computer)
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# 2. Initialize Git if needed
git init

# 3. Stage and commit files
git add .
git commit -m "Initial commit"

# 4. Rename the current branch
git branch -M main

# 5. Add the Bitbucket remote
git remote add origin https://x-token-auth@bitbucket.org/<workspace-id>/<repo-name>.git

# If origin already exists, use this instead:
# git remote set-url origin https://x-token-auth@bitbucket.org/<workspace-id>/<repo-name>.git

# 6. Push and set upstream
git push -u origin main

# 7. Later updates
git add .
git commit -m "Describe your changes"
git push
```

**Remember:** Create the appropriate token, grant the minimum required permissions, and enter the token only at the secure credential prompt. Do not commit or expose the token.
