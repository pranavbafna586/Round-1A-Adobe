# PDF Outline Extractor

A Python-based tool that extracts document structure (title and hierarchical headings) from PDF files using font size analysis. The tool identifies and categorizes text elements as titles, H1, H2, and H3 headings based on their font sizes and positions within the document.

## Features

- **Automatic Title Detection**: Identifies the main title from the first page using the largest font size
- **Hierarchical Heading Extraction**: Detects H1, H2, and H3 headings throughout the document
- **Multi-line Text Handling**: Properly combines text that spans multiple lines
- **Word Break Repair**: Fixes hyphenated words broken across lines
- **Noise Filtering**: Removes common document artifacts and irrelevant text
- **JSON Output**: Structured output format for easy integration with other tools
- **Docker Support**: Containerized execution for consistent deployment

## Project Structure

```
├── main.py                 # Main processing script
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── README.md              # Project documentation
├── input/                 # Directory for input PDF files
├── output/                # Directory for generated JSON files
└── utils/                 # Utility modules
    ├── heading_detector.py # Heading level detection logic
    └── pdf_utils.py       # PDF text extraction utilities
```

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Docker (optional, for containerized execution)

### Local Installation

1. Clone or download the project files
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Docker Installation

1. Build the Docker image:
   ```bash
   docker build -t pdf_extractor .
   ```

## Usage

### Method 1: Direct Python Execution

1. Place your PDF files in the `input/` directory
2. Run the extraction script:
   ```bash
   python main.py
   ```
3. Check the `output/` directory for generated JSON files

### Method 2: Docker Execution

1. Place your PDF files in the `input/` directory
2. Run the Docker container:
   ```bash
   docker run -v %cd%/input:/app/input -v %cd%/output:/app/output pdf_extractor
   ```

## Output Format

The tool generates JSON files with the following structure:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "First Level Heading",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Second Level Heading",
      "page": 2
    },
    {
      "level": "H3",
      "text": "Third Level Heading",
      "page": 2
    }
  ]
}
```

### Fields Description

- `title`: The main title of the document (extracted from the first page)
- `outline`: Array of heading objects containing:
  - `level`: Heading hierarchy level (H1, H2, or H3)
  - `text`: The actual heading text content
  - `page`: Page number where the heading appears

## Algorithm Overview

### Title Extraction

1. Analyzes the first page of the PDF
2. Identifies text with the largest font size
3. Combines multi-line titles that may be split across lines
4. Filters out common noise words and artifacts

### Heading Detection

1. Scans all pages for text elements with varying font sizes
2. Groups consecutive lines with the same font size (multi-line headings)
3. Establishes font size thresholds for H1, H2, and H3 classification
4. Assigns heading levels based on relative font sizes
5. Removes duplicate headings and noise

### Text Processing

- **Word Break Repair**: Reconstructs words split by hyphens across lines
- **Whitespace Normalization**: Standardizes spacing and removes excess whitespace
- **Noise Filtering**: Excludes common document elements like page numbers, headers, and footers

## Technical Dependencies

- **PyMuPDF (fitz)**: PDF parsing and text extraction library
- **Python Standard Library**: Collections, regex, os, json modules

## Limitations

- Works best with well-formatted PDFs that use consistent font sizing for headings
- May struggle with documents that don't follow standard heading conventions
- Performance depends on PDF complexity and size
- Currently supports only text-based PDFs (not scanned images)

## Contributing

When modifying the code:

1. Maintain consistent code formatting and documentation
2. Test with various PDF formats and structures
3. Update this README if adding new features or changing functionality
4. Ensure Docker compatibility is maintained

## License

This project is provided as-is for educational and development purposes.
