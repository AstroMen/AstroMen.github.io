import os
import re
import yaml
from pathlib import Path
from slugify import slugify  # pip install python-slugify

POSTS_DIR = "_posts"
TAGS_DIR = "tag"
LAYOUT = "tag"

os.makedirs(TAGS_DIR, exist_ok=True)

def extract_tags_from_post(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract YAML front matter
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return []

    front_matter = yaml.safe_load(match.group(1))
    return front_matter.get("tags", [])

# Collect unique tags
all_tags = set()
for filename in os.listdir(POSTS_DIR):
    if filename.endswith(".md"):
        path = os.path.join(POSTS_DIR, filename)
        tags = extract_tags_from_post(path)
        all_tags.update(tags)

# Generate tag pages
for tag in sorted(all_tags):
    slug = slugify(tag)
    tag_file_path = os.path.join(TAGS_DIR, f"{slug}.md")
    with open(tag_file_path, "w", encoding="utf-8") as f:
        f.write(f"""---
layout: {LAYOUT}
title: "Tag: {tag}"
tag: {tag}
permalink: /tag/{slug}/
---
""")
print(f"✅ Generated {len(all_tags)} tag pages in '{TAGS_DIR}/'")