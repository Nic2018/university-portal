# Git Commit Guide for Software Integration Documentation

## Overview
This guide explains how to commit code to GitHub for the university portal project.

## Prerequisites
- Git installed on your system
- GitHub account configured
- Repository cloned locally

## Step-by-Step Process

### Step 1: Check Current Status
```bash
git status
```
**What it does:** Shows which files have been modified, added, or deleted.

**Screenshot Tip:** Capture the terminal output showing:
- Modified files (in red)
- Untracked files (in red)
- Current branch name

---

### Step 2: Add Files to Staging Area
```bash
# Add a specific file
git add filename.py

# Add multiple specific files
git add file1.py file2.py file3.md

# Add all files in current directory
git add .

# Add all Python files
git add *.py
```
**What it does:** Marks files to be included in the next commit.

**Screenshot Tip:** After running `git add`, run `git status` again to show files in green (staged).

---

### Step 3: Commit Changes
```bash
git commit -m "Your descriptive commit message"
```
**What it does:** Saves your staged changes to the local repository with a message.

**Good commit message examples:**
- ✅ "Add user authentication feature"
- ✅ "Fix login bug for admin users"
- ✅ "Update README with installation instructions"
- ❌ "changes" (too vague)
- ❌ "stuff" (not descriptive)

**Screenshot Tip:** Capture the commit confirmation showing:
- Number of files changed
- Insertions/deletions count
- Commit hash

---

### Step 4: Push to GitHub
```bash
git push origin main
```
**What it does:** Uploads your local commits to GitHub (remote repository).

**Screenshot Tip:** Capture the push output showing:
- Branch being pushed
- Objects being compressed
- Success message

---

### Step 5: Verify on GitHub
1. Open your browser
2. Go to `https://github.com/Nic2018/university-portal`
3. Check that your commits appear in the commit history

**Screenshot Tip:** Capture:
- GitHub repository page showing recent commits
- Commit history page
- Individual commit details showing file changes

---

## Common Scenarios

### Scenario 1: First-time commit of new files
```bash
git status                          # Check what's new
git add .                           # Add all new files
git commit -m "Initial commit"      # Commit with message
git push origin main                # Push to GitHub
```

### Scenario 2: Updating existing files
```bash
git status                                    # See what changed
git add filename.py                           # Add specific file
git commit -m "Update login validation"       # Commit
git push origin main                          # Push
```

### Scenario 3: Adding documentation
```bash
git add README.md USER_GUIDE.md
git commit -m "Add project documentation"
git push origin main
```

---

## Visual Workflow Diagram

```
Working Directory  →  Staging Area  →  Local Repo  →  Remote Repo (GitHub)
   (Your files)        (git add)       (git commit)     (git push)
```

---

## Important Notes

### What to Commit
✅ Source code files (.py, .html, .css, .js)
✅ Documentation (.md, .txt)
✅ Configuration files (settings.py, requirements.txt)
✅ Static assets (images, CSS, JS)

### What NOT to Commit
❌ Database files (db.sqlite3)
❌ Virtual environments (.venv, venv)
❌ IDE settings (.vscode, .idea)
❌ Sensitive data (passwords, API keys)
❌ Large binary files (unless necessary)

### Using .gitignore
Create a `.gitignore` file to automatically exclude files:
```
# Python
*.pyc
__pycache__/
.venv/
venv/

# Django
db.sqlite3
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## Checking Your Work

### View Commit History
```bash
git log                    # Full history
git log --oneline          # Compact view
git log -n 5               # Last 5 commits
```

### View Changes Before Committing
```bash
git diff                   # See unstaged changes
git diff --staged          # See staged changes
```

### Undo Mistakes
```bash
# Unstage a file (before commit)
git restore --staged filename.py

# Discard changes to a file
git restore filename.py

# Amend last commit message
git commit --amend -m "New message"
```

---

## For Your Report

### Screenshots to Include:
1. **Terminal showing `git status`** - Before adding files
2. **Terminal showing `git add`** - Adding files to staging
3. **Terminal showing `git status`** - After adding (files in green)
4. **Terminal showing `git commit`** - Commit with message
5. **Terminal showing `git push`** - Pushing to GitHub
6. **GitHub website** - Repository page showing commits
7. **GitHub website** - Individual commit details
8. **GitHub website** - File changes in commit

### Explanation Points:
- **Version Control**: Git tracks changes over time
- **Collaboration**: Multiple developers can work together
- **Backup**: Code is stored remotely on GitHub
- **History**: Can view and revert to previous versions
- **Branching**: Can work on features separately (advanced)

---

## Example for Your University Portal

```bash
# 1. Check status
git status

# 2. Add documentation files
git add README.md USER_GUIDE.md BLACK_BOX_TESTING.md

# 3. Commit with descriptive message
git commit -m "Add project documentation and testing guide"

# 4. Push to GitHub
git push origin main

# 5. Verify on GitHub at:
# https://github.com/Nic2018/university-portal/commits/main
```

---

## Troubleshooting

### "Permission denied"
- Check your GitHub credentials
- Use SSH key or personal access token

### "Merge conflict"
- Pull latest changes first: `git pull origin main`
- Resolve conflicts manually
- Then commit and push

### "Nothing to commit"
- No changes were made
- Or files weren't added to staging area

---

## Additional Resources
- [GitHub Docs](https://docs.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Visualizing Git](https://git-school.github.io/visualizing-git/)
