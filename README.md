# AstroMen.github.io

This blog contains technical posts covering a wide range of topics, including **fundamental knowledge, architecture design, and practical implementation details**.  
It is built with **Jekyll**, allowing clean and customizable publishing of articles with code snippets, diagrams, and structured documentation.  
The goal is to provide a space for sharing insights, best practices, and lessons learned in software engineering and system design.

### Jekyll Blog Setup on macOS with Ruby via rbenv

This guide documents the steps to set up and run a Jekyll blog on macOS using **Ruby 3.4.5** managed by rbenv.

---

#### Prerequisites

- **Homebrew** installed  
- **rbenv** for managing Ruby versions  
- macOS terminal with **zsh** (default on macOS Catalina and later)

#### Setup Steps

##### 1. Install Homebrew (if not already installed)
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

##### 2. Install rbenv and ruby-build
```
brew update
brew install rbenv ruby-build
```

Initialize rbenv (for zsh):
```
echo 'eval "$(rbenv init - zsh)"' >> ~/.zshrc
source ~/.zshrc
```

##### 3. Install Ruby 3.4.5
```
rbenv install 3.4.5
rbenv global 3.4.5
rbenv rehash
ruby -v
```

You should see:
```
ruby 3.4.5 (xxxx revision xxxx) [arm64-darwin23]
```

##### 4. Install required system dependencies
```
brew install pkg-config protobuf
protoc --version
```

#### Project Setup

##### 1. Create a `Gemfile`
```
source "https://rubygems.org"

gem "jekyll", "~> 4.3.2"
gem "minima", "~> 2.5"
gem "jekyll-feed", "~> 0.12"
gem "jekyll-paginate", "~> 1.1"
gem "csv"
gem "logger"
gem "base64"
```

##### 2. Install Bundler and Gems
```
gem install bundler
rbenv rehash
bundle install
rbenv rehash
```

If you face issues with old Bundler versions, uninstall and update:
```
gem uninstall bundler -v 1.17.2
gem update --system
rbenv rehash
bundle install
rbenv rehash
```

#### Running Jekyll Locally
Start the Jekyll server:
```
bundle exec jekyll serve
```

Then open your browser and visit:
```
http://localhost:4000
```

#### Troubleshooting

- If Ruby version does not update after installation:
  ```
  which ruby
  ```
  Ensure it points to:
  ```
  ~/.rbenv/shims/ruby
  ```
  If not, add this to your `~/.zshrc`:
  ```
  export PATH="$HOME/.rbenv/shims:$PATH"
  eval "$(rbenv init - zsh)"
  ```

- If gems are outdated, clean and reinstall:
  ```
  bundle clean --force
  rm Gemfile.lock
  bundle install
  rbenv rehash
  ```

---

#### Useful Commands Reference
```
ruby -v                  # Check Ruby version
rbenv install -l         # List all Ruby versions
rbenv global 3.4.5       # Set global Ruby version
rbenv rehash             # Refresh shims after installs
bundle -v                # Check Bundler version
gem list bundler         # Check installed Bundler versions
```

---

#### Tag Page Generator for Jekyll

A Python script to generate tag pages for a Jekyll blog automatically.

##### 📦 Installation

Install the required dependency:
```bash
pip install python-slugify
```

##### ▶️ Usage

Run the script with:
```bash
python generate_tag_pages.py
```

##### ⚙️ What This Script Does
- Traverses the `_posts/` directory  
- Extracts all `tags` from each post  
- Generates a Markdown file for each tag in the `tag/` directory (e.g. `tag/data-science.md`)  
- These tag files can be used by **Jekyll** to build tag archive pages

##### 📁 Output
Each generated tag file will be in the format:
```markdown
---
layout: tag
title: "Tag: data-science"
tag: data-science
---
```
These files will be placed in the `tag/` folder and picked up by Jekyll during site build.
