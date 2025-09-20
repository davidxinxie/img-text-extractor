# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an image content recognition tool that automatically analyzes images using OpenAI Vision API and writes descriptions to image metadata for macOS Spotlight search. The tool supports both normal image analysis and specialized screenshot text extraction mode.

## Architecture

The codebase consists of four main modules:

- `main.py` - CLI entry point and orchestration logic
- `vision.py` - OpenAI Vision API integration for image analysis
- `metadata.py` - Metadata writing using exiftool and keyword extraction
- `config.py` - Configuration management and prompts
- `github_sync.py` - GitHub API integration for automated repository updates

## Key Dependencies

- **exiftool** (system dependency): `brew install exiftool`
- **OpenAI API**: Requires `OPENAI_API_KEY` in `.env` file
- **Python packages**: See `requirements.txt`

## Common Commands

### Setup
```bash
# Automated setup (recommended)
./setup.sh

# Manual setup
brew install exiftool
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add your OpenAI API key
chmod +x main.py
```

### Running the Tool
```bash
# Basic usage - process all images in directory
./main.py ~/Pictures

# Process single image file
./main.py ~/Pictures/image.jpg

# Process multiple directories and files
./main.py ~/Pictures ~/Screenshots/screen.png

# Preview mode - analyze but don't write metadata
./main.py ~/Pictures --dry-run

# Screenshot mode - optimized for text extraction
./main.py ~/Screenshots --screenshot-mode
./main.py ~/Screenshots/screen.png --screenshot-mode --dry-run

# Force reprocess images with existing metadata
./main.py ~/Pictures --force

# Safe mode with extra backups
./main.py ~/Pictures --safe-mode

# Non-recursive (current directory only)
./main.py ~/Pictures --no-recursive

# Verify existing metadata
./main.py ~/Pictures --verify
```

### Testing
```bash
# Run complete test suite (recommended)
./run_tests.sh

# Run tests manually with unittest
python test_main.py
python -m unittest test_main.py

# Run specific test class
python -m unittest test_main.TestFindImages
```

## Important Implementation Details

### Metadata Strategy
The tool writes to multiple metadata fields to ensure Spotlight compatibility:
- `Subject` and `Caption-Abstract`: Search-optimized short descriptions
- `ImageDescription` and `UserComment`: Full structured descriptions  
- `XMP:Description` and `Keywords`: Extracted keywords for search
- Screenshot mode adds `XMP:Title` (text content) and `Software` (app info)

### File Safety
- Creates temporary backups before modification
- Preserves original file timestamps
- Validates file integrity after operations
- Uses exiftool's built-in backup mechanism

### Two Analysis Modes
1. **Normal mode**: General image content analysis (scene, objects, colors, style)
2. **Screenshot mode**: Text extraction and UI element recognition

### Prompt Engineering
Structured prompts in `config.py` ensure consistent output format for metadata extraction. Screenshot mode uses specialized prompts optimized for text recognition.

## Configuration Notes

- **Supported formats**: JPG, PNG, WebP, GIF, HEIC/HEIF (requires pillow-heif)
- **AI Model**: Uses gpt-4o-mini for cost-effective analysis
- **Image processing**: Images are resized to max 1024x1024 to reduce API costs
- **Keywords**: Limited to 15 (normal) or 25 (screenshot mode) 
- **Platform**: macOS only (uses Spotlight and mdimport for indexing)
- **Language**: Bilingual support (Chinese/English) in setup and error messages
- **Python**: Requires Python 3.8+ (tested with Python 3.x)

## Development Workflow

### Processing Architecture
- **Lazy initialization**: ImageAnalyzer only created when needed to avoid API key validation for metadata-only operations
- **Per-image processing**: Processes images individually rather than batch pre-checking for better progress feedback
- **Error isolation**: Individual image failures don't stop entire batch processing

### Test Coverage
The test suite (`test_main.py`) uses Python unittest framework and covers:
- **File discovery**: Image file finding (recursive/non-recursive modes)
- **Processing logic**: Individual image processing workflows
- **Metadata handling**: Verification and skip logic for existing metadata
- **CLI arguments**: All command-line options (--dry-run, --force, --verify, --screenshot-mode)
- **Error handling**: Edge cases and failure scenarios
- **Architecture**: ImageAnalyzer lazy initialization to avoid API key validation for metadata-only operations

### Common Development Commands
```bash
# Make main.py executable after changes
chmod +x main.py

# Test with sample images without API calls
./main.py ~/Pictures --verify

# Debug specific functionality
python -c "from main import find_images; print(find_images('test_dir', recursive=False))"
```

### GitHub Automation Commands
```bash
# Setup GitHub Personal Access Token
./github_sync.py setup

# Test GitHub API connection
./github_sync.py test

# Upload single file to GitHub
./github_sync.py upload --file README.md --github-path README.md --message "Update documentation"

# Sync entire repository to GitHub
./github_sync.py sync --message "Auto-sync repository updates"

# Force update existing file
./github_sync.py upload --file config.py --github-path config.py --message "Update config" --force
```