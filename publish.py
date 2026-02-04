#!/usr/bin/env python3
"""
Obsidian Publishing Script
A cross-platform Python script for publishing articles from Obsidian.
"""

import argparse
import os
import sys
from pathlib import Path
import yaml
import re
from datetime import datetime
from typing import Dict, List, Optional


class ObsidianPublisher:
    """Main class for publishing Obsidian articles."""
    
    def __init__(self, vault_path: str, output_path: str = None):
        """
        Initialize the publisher.
        
        Args:
            vault_path: Path to the Obsidian vault
            output_path: Path to output directory (default: ./output)
        """
        self.vault_path = Path(vault_path).resolve()
        self.output_path = Path(output_path or "./output").resolve()
        
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")
        
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def extract_frontmatter(self, content: str) -> tuple[Optional[Dict], str]:
        """
        Extract YAML frontmatter from markdown content.
        
        Args:
            content: Markdown file content
            
        Returns:
            Tuple of (frontmatter dict, content without frontmatter)
        """
        # Check for YAML frontmatter (between --- markers)
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
                content_without_fm = match.group(2)
                return frontmatter, content_without_fm
            except yaml.YAMLError as e:
                print(f"Warning: Failed to parse frontmatter: {e}")
                return None, content
        
        return None, content
    
    def process_markdown_links(self, content: str) -> str:
        """
        Convert Obsidian-style wiki links to standard markdown links.
        
        Args:
            content: Markdown content with wiki links
            
        Returns:
            Content with standard markdown links
        """
        # Convert [[Link]] to [Link](Link.md)
        content = re.sub(r'\[\[([^\]|]+)\]\]', r'[\1](\1.md)', content)
        
        # Convert [[Link|Display Text]] to [Display Text](Link.md)
        content = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'[\2](\1.md)', content)
        
        return content
    
    def publish_file(self, file_path: Path, process_links: bool = True) -> Dict:
        """
        Publish a single markdown file.
        
        Args:
            file_path: Path to the markdown file
            process_links: Whether to process wiki links
            
        Returns:
            Dictionary with publication metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() != '.md':
            raise ValueError(f"Not a markdown file: {file_path}")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter
        frontmatter, body = self.extract_frontmatter(content)
        
        # Process links if enabled
        if process_links:
            body = self.process_markdown_links(body)
        
        # Determine output filename
        relative_path = file_path.relative_to(self.vault_path)
        output_file = self.output_path / relative_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write processed content
        output_content = ""
        if frontmatter:
            output_content = "---\n" + yaml.dump(frontmatter) + "---\n\n"
        output_content += body
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        return {
            'source': str(file_path),
            'output': str(output_file),
            'frontmatter': frontmatter,
            'timestamp': datetime.now().isoformat()
        }
    
    def publish_vault(self, pattern: str = "**/*.md", process_links: bool = True) -> List[Dict]:
        """
        Publish all markdown files in the vault matching the pattern.
        
        Args:
            pattern: Glob pattern for files to publish
            process_links: Whether to process wiki links
            
        Returns:
            List of publication metadata dictionaries
        """
        results = []
        files = list(self.vault_path.glob(pattern))
        
        if not files:
            print(f"No files found matching pattern: {pattern}")
            return results
        
        for file_path in files:
            try:
                result = self.publish_file(file_path, process_links)
                results.append(result)
                print(f"Published: {file_path.name} -> {result['output']}")
            except Exception as e:
                print(f"Error publishing {file_path}: {e}")
        
        return results


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Publish articles from Obsidian vault',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/vault
  %(prog)s /path/to/vault -o /path/to/output
  %(prog)s /path/to/vault -f article.md
  %(prog)s /path/to/vault --no-process-links
        """
    )
    
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault directory'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./output',
        help='Output directory (default: ./output)'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Publish a specific file instead of the entire vault'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        default='**/*.md',
        help='Glob pattern for files to publish (default: **/*.md)'
    )
    
    parser.add_argument(
        '--no-process-links',
        action='store_true',
        help='Do not convert wiki links to markdown links'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        publisher = ObsidianPublisher(args.vault_path, args.output)
        
        if args.file:
            # Publish single file
            file_path = Path(args.vault_path) / args.file
            result = publisher.publish_file(file_path, not args.no_process_links)
            print(f"\nSuccessfully published to: {result['output']}")
        else:
            # Publish entire vault or pattern
            results = publisher.publish_vault(args.pattern, not args.no_process_links)
            print(f"\nSuccessfully published {len(results)} file(s)")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
