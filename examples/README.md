# Example Obsidian Vault

This directory contains sample markdown files that demonstrate the publishing script's capabilities.

## Files

- `getting-started.md` - A beginner's guide with frontmatter and wiki links
- `advanced-topics.md` - An advanced guide with code examples

## Testing the Script

From the repository root, run:

```bash
python publish.py examples/sample_vault
```

This will publish all markdown files to the `./output` directory.

## Output

The published files will:
- Preserve YAML frontmatter
- Convert wiki links to standard markdown links
- Maintain directory structure
