"""
Tests for Obsidian Publishing Script
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from publish import ObsidianPublisher


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary Obsidian vault for testing."""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    return vault


@pytest.fixture
def temp_output(tmp_path):
    """Create a temporary output directory for testing."""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def sample_markdown():
    """Sample markdown content without frontmatter."""
    return """# Test Article

This is a test article with some content.

## Section 1

Some text here.
"""


@pytest.fixture
def sample_markdown_with_frontmatter():
    """Sample markdown content with frontmatter."""
    return """---
title: Test Article
author: Test Author
date: 2024-01-01
tags:
  - test
  - article
---

# Test Article

This is a test article with frontmatter.
"""


@pytest.fixture
def sample_markdown_with_links():
    """Sample markdown with Obsidian wiki links."""
    return """# Test Article

This article links to [[Another Article]].

It also has a link with custom text: [[Another Article|custom text]].

Standard markdown links work too: [Link](https://example.com)
"""


class TestObsidianPublisher:
    """Tests for ObsidianPublisher class."""
    
    def test_init_creates_output_directory(self, temp_vault, tmp_path):
        """Test that initialization creates output directory."""
        output = tmp_path / "new_output"
        publisher = ObsidianPublisher(str(temp_vault), str(output))
        assert output.exists()
        assert publisher.vault_path == temp_vault
        assert publisher.output_path == output
    
    def test_init_with_nonexistent_vault_raises_error(self, tmp_path):
        """Test that initialization with non-existent vault raises error."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(ValueError, match="Vault path does not exist"):
            ObsidianPublisher(str(nonexistent))
    
    def test_extract_frontmatter_with_valid_yaml(self, sample_markdown_with_frontmatter):
        """Test extracting valid YAML frontmatter."""
        publisher = ObsidianPublisher(str(Path.cwd()))
        frontmatter, content = publisher.extract_frontmatter(sample_markdown_with_frontmatter)
        
        assert frontmatter is not None
        assert frontmatter['title'] == 'Test Article'
        assert frontmatter['author'] == 'Test Author'
        # YAML may parse date as datetime.date object or string
        assert 'date' in frontmatter
        assert 'test' in frontmatter['tags']
        assert '# Test Article' in content
    
    def test_extract_frontmatter_without_frontmatter(self, sample_markdown):
        """Test extracting frontmatter from content without it."""
        publisher = ObsidianPublisher(str(Path.cwd()))
        frontmatter, content = publisher.extract_frontmatter(sample_markdown)
        
        assert frontmatter is None
        assert content == sample_markdown
    
    def test_process_markdown_links_simple(self):
        """Test processing simple wiki links."""
        publisher = ObsidianPublisher(str(Path.cwd()))
        content = "This links to [[Another Article]]."
        result = publisher.process_markdown_links(content)
        
        assert result == "This links to [Another Article](Another Article.md)."
    
    def test_process_markdown_links_with_display_text(self):
        """Test processing wiki links with custom display text."""
        publisher = ObsidianPublisher(str(Path.cwd()))
        content = "This has [[Another Article|custom text]]."
        result = publisher.process_markdown_links(content)
        
        assert result == "This has [custom text](Another Article.md)."
    
    def test_process_markdown_links_preserves_standard_links(self):
        """Test that standard markdown links are preserved."""
        publisher = ObsidianPublisher(str(Path.cwd()))
        content = "Standard [link](https://example.com) here."
        result = publisher.process_markdown_links(content)
        
        assert result == content
    
    def test_publish_file_creates_output(self, temp_vault, temp_output, sample_markdown):
        """Test publishing a single file creates output."""
        # Create a test file
        test_file = temp_vault / "test.md"
        test_file.write_text(sample_markdown)
        
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        result = publisher.publish_file(test_file)
        
        assert result['source'] == str(test_file)
        assert Path(result['output']).exists()
        assert 'timestamp' in result
    
    def test_publish_file_with_frontmatter(self, temp_vault, temp_output, sample_markdown_with_frontmatter):
        """Test publishing a file with frontmatter."""
        test_file = temp_vault / "test.md"
        test_file.write_text(sample_markdown_with_frontmatter)
        
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        result = publisher.publish_file(test_file)
        
        assert result['frontmatter'] is not None
        assert result['frontmatter']['title'] == 'Test Article'
        
        # Verify output file contains frontmatter
        output_file = Path(result['output'])
        content = output_file.read_text()
        assert '---' in content
        assert 'title: Test Article' in content
    
    def test_publish_file_processes_links(self, temp_vault, temp_output, sample_markdown_with_links):
        """Test that publishing processes wiki links."""
        test_file = temp_vault / "test.md"
        test_file.write_text(sample_markdown_with_links)
        
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        result = publisher.publish_file(test_file, process_links=True)
        
        output_file = Path(result['output'])
        content = output_file.read_text()
        
        assert '[Another Article](Another Article.md)' in content
        assert '[custom text](Another Article.md)' in content
    
    def test_publish_file_without_processing_links(self, temp_vault, temp_output, sample_markdown_with_links):
        """Test that publishing can skip link processing."""
        test_file = temp_vault / "test.md"
        test_file.write_text(sample_markdown_with_links)
        
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        result = publisher.publish_file(test_file, process_links=False)
        
        output_file = Path(result['output'])
        content = output_file.read_text()
        
        assert '[[Another Article]]' in content
    
    def test_publish_file_with_nonexistent_file_raises_error(self, temp_vault, temp_output):
        """Test that publishing non-existent file raises error."""
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        nonexistent = temp_vault / "nonexistent.md"
        
        with pytest.raises(FileNotFoundError):
            publisher.publish_file(nonexistent)
    
    def test_publish_file_with_non_markdown_raises_error(self, temp_vault, temp_output):
        """Test that publishing non-markdown file raises error."""
        test_file = temp_vault / "test.txt"
        test_file.write_text("Not markdown")
        
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        
        with pytest.raises(ValueError, match="Not a markdown file"):
            publisher.publish_file(test_file)
    
    def test_publish_vault_publishes_all_markdown_files(self, temp_vault, temp_output, sample_markdown):
        """Test publishing entire vault publishes all markdown files."""
        # Create multiple test files
        (temp_vault / "test1.md").write_text(sample_markdown)
        (temp_vault / "test2.md").write_text(sample_markdown)
        subdir = temp_vault / "subdir"
        subdir.mkdir()
        (subdir / "test3.md").write_text(sample_markdown)
        
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        results = publisher.publish_vault()
        
        assert len(results) == 3
        assert all('output' in r for r in results)
    
    def test_publish_vault_with_pattern(self, temp_vault, temp_output, sample_markdown):
        """Test publishing vault with specific pattern."""
        # Create test files in different directories
        (temp_vault / "keep.md").write_text(sample_markdown)
        (temp_vault / "skip.md").write_text(sample_markdown)
        subdir = temp_vault / "articles"
        subdir.mkdir()
        (subdir / "article.md").write_text(sample_markdown)
        
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        results = publisher.publish_vault(pattern="articles/*.md")
        
        assert len(results) == 1
        assert 'article.md' in results[0]['output']
    
    def test_publish_vault_with_no_files_returns_empty(self, temp_vault, temp_output):
        """Test publishing vault with no matching files returns empty list."""
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        results = publisher.publish_vault()
        
        assert len(results) == 0
    
    def test_cross_platform_path_handling(self, temp_vault, temp_output, sample_markdown):
        """Test that paths work correctly across platforms."""
        # Create nested directory structure
        nested = temp_vault / "level1" / "level2"
        nested.mkdir(parents=True)
        test_file = nested / "test.md"
        test_file.write_text(sample_markdown)
        
        publisher = ObsidianPublisher(str(temp_vault), str(temp_output))
        result = publisher.publish_file(test_file)
        
        # Verify output preserves directory structure
        output_path = Path(result['output'])
        assert output_path.exists()
        assert output_path.parent.name == "level2"
        assert output_path.parent.parent.name == "level1"


class TestCLI:
    """Tests for command-line interface."""
    
    def test_cli_help(self):
        """Test that CLI help works."""
        import subprocess
        result = subprocess.run(
            ['python', 'publish.py', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Publish articles from Obsidian vault' in result.stdout
    
    def test_cli_version(self):
        """Test that CLI version works."""
        import subprocess
        result = subprocess.run(
            ['python', 'publish.py', '--version'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '1.0.0' in result.stdout or '1.0.0' in result.stderr
