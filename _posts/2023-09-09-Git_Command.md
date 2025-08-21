---
layout: post
title:  "Git Command Help Documentation"
date:   2023-09-09
categories: jekyll update
tags: 
  - Version Control
lang: en
---

## Introduction

Git is a distributed version control system that helps track changes in source code during software development. It allows multiple people to work on the same project simultaneously, ensuring changes are tracked and merge conflicts are handled efficiently. Here is a guide that encompasses the various commands and scenarios we discussed.

## Setting Up Your Repository

### Initializing a Repository
To create a new repository in your current directory, use:
```
git init
```

### Cloning an Existing Repository
To clone an existing repository, use:
```
git clone REPO_URL
```

## Branch Management

### Viewing Existing Branches
To view existing branches in your repository, use:
```
git branch
```

### Creating a New Branch
To create a new branch, use:
```
git checkout -b BRANCH_NAME
```

## Making Changes

### Adding Changes
To add changes to your staging area, use:
```
git add FILENAME
```
or to add all changes, use:
```
git add .
```

### Committing Changes
To commit changes in the staging area, use:
```
git commit -m "COMMIT_MESSAGE"
```

## Pushing Changes

### Setting Upstream Branch and Pushing Changes
When pushing a branch for the first time, set the upstream branch using:
```
git push --set-upstream REMOTE_URL BRANCH_NAME
```

### Pushing Changes Normally
For subsequent pushes, use:
```
git push REMOTE_URL BRANCH_NAME
```
REMOTE_URL: https://[username]:[token]@[git_url_without_https]


## Handling Errors and Troubleshooting

### Error: src refspec master does not match any
This error occurs when trying to push to a non-existent branch. Ensure the branch exists locally by using git branch to list existing branches.

### Error: Authentication Failed
This error occurs when the authentication details are incorrect. Make sure to update your credentials in the repository settings, and consider using Personal Access Tokens (PATs) instead of passwords.

### Forcing Push (With Caution)
To force push (overwrite remote branch with local branch), use:
```
git push -f REMOTE_URL BRANCH_NAME
```

## Rolling Back Changes

### Reverting a Commit
To revert a specific commit, use:
```
git revert COMMIT_HASH
```

### Resetting a Branch
To reset your branch to a specific commit, use:
```
git reset --hard COMMIT_HASH
```

## Security Notice

Please be advised to keep your Personal Access Tokens and passwords confidential to prevent unauthorized access to your repositories. Always use secure channels to share sensitive information.
