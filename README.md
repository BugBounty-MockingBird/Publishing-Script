# Publishing-Script

[![Python Tests](https://github.com/BugBounty-MockingBird/Publishing-Script/workflows/Python%20Tests/badge.svg)](https://github.com/BugBounty-MockingBird/Publishing-Script/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Cross-platform Python script for publishing articles from Obsidian vaults.

## Features

- 🚀 **Cross-platform**: Works on Windows, macOS, and Linux
- 📝 **YAML Frontmatter**: Extracts and preserves YAML frontmatter from markdown files
- 🔗 **Wiki Link Conversion**: Converts Obsidian wiki links (`[[Link]]`) to standard markdown links
- 📂 **Batch Processing**: Publish entire vaults or specific files
- 🎯 **Pattern Matching**: Use glob patterns to select files to publish
- 🛠️ **CLI Interface**: Simple command-line interface for easy integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/BugBounty-MockingBird/Publishing-Script.git
cd Publishing-Script
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Publish an entire Obsidian vault:
```bash
python publish.py /path/to/obsidian/vault
```

Specify output directory:
```bash
python publish.py /path/to/obsidian/vault -o /path/to/output
```

### Publish Specific Files

Publish a single file:
```bash
python publish.py /path/to/obsidian/vault -f article.md
```

Publish files matching a pattern:
```bash
python publish.py /path/to/obsidian/vault -p "articles/*.md"
```

### Options

```
usage: publish.py [-h] [-o OUTPUT] [-f FILE] [-p PATTERN] [--no-process-links] [-v] vault_path

Publish articles from Obsidian vault

positional arguments:
  vault_path            Path to the Obsidian vault directory

optional arguments:
  -h, --help            Show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory (default: ./output)
  -f FILE, --file FILE  Publish a specific file instead of the entire vault
  -p PATTERN, --pattern PATTERN
                        Glob pattern for files to publish (default: **/*.md)
  --no-process-links    Do not convert wiki links to markdown links
  -v, --version         Show program's version number and exit
```

## Features in Detail

### Frontmatter Support

The script recognizes and preserves YAML frontmatter in your markdown files:

```markdown
---
title: My Article
author: John Doe
date: 2024-01-01
tags:
  - python
  - obsidian
---

# My Article Content
```

### Wiki Link Conversion

Obsidian wiki links are automatically converted to standard markdown links:

- `[[Another Article]]` → `[Another Article](Another Article.md)`
- `[[Another Article|custom text]]` → `[custom text](Another Article.md)`

Use `--no-process-links` to disable this behavior.

## Development

### Running Tests

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=publish --cov-report=html
```

### Running Tests Across Platforms

The GitHub Actions workflow automatically tests the script on:
- Ubuntu (Linux)
- Windows
- macOS

With Python versions:
- 3.9
- 3.10
- 3.11
- 3.12

## Requirements

- Python 3.9 or higher
- PyYAML 6.0 or higher

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Bug Bounty KSP
