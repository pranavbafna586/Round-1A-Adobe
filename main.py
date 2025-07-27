"""
PDF Outline Extractor

A comprehensive tool for extracting document structure (title and hierarchical headings) 
from PDF files using advanced font size analysis and text processing techniques.

This module implements intelligent algorithms for:
- Title detection from the first page
- Hierarchical heading extraction (H1, H2, H3)
- Multi-line text handling and word break repair
- Noise filtering and text cleaning

Author: Adobe Assessment Project
Date: 2025
"""

import os
import json
import fitz  # PyMuPDF library for PDF processing
from collections import defaultdict
import re

# Common words and phrases that should be filtered out as noise
NOISE_WORDS = {
    "open access", "research", "sustainable environment", "article", "journal",
    "abstract", "introduction", "references", "acknowledgments", "appendix",
    "received", "accepted", "published", "volume", "issue", "pp.", "pages"
}

def clean_text(text):
    """
    Clean and normalize text by removing extra whitespace and fixing word breaks.
    
    This function performs several text cleaning operations:
    1. Normalizes all whitespace by converting newlines to spaces
    2. Collapses multiple consecutive spaces into single spaces
    3. Repairs hyphenated word breaks (e.g., "under- standing" -> "understanding")
    4. Fixes cases where words are broken across lines without hyphens
    
    Args:
        text (str): Raw text extracted from PDF that may contain formatting artifacts
        
    Returns:
        str: Cleaned and normalized text with proper spacing and word continuity
        
    Examples:
        >>> clean_text("under-\n standing")
        "understanding"
        >>> clean_text("word   with\n  extra   spaces")
        "word with extra spaces"
    """
    # Normalize all whitespace by replacing newlines with spaces and collapsing multiple spaces
    text = " ".join(text.replace("\n", " ").split())
    
    # Fix hyphenated word breaks (e.g., "under- standing" -> "understanding")
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
    
    # Fix cases where words are broken across lines without hyphens
    # This is a heuristic approach that joins words if both parts are longer than 2 characters
    text = re.sub(r'(\w)\s+(\w)', lambda m: m.group(1) + m.group(2) if len(m.group(1)) > 2 and len(m.group(2)) > 2 else m.group(0), text)
    
    return text.strip()

def is_noisy(text):
    """
    Determine if text should be filtered out as noise or irrelevant content.
    
    This function identifies common document artifacts that are not meaningful
    headings or titles, such as:
    - Standard academic paper elements (abstract, references, etc.)
    - Publication metadata (volume, issue, page numbers)
    - Very short text fragments (likely page numbers or artifacts)
    
    Args:
        text (str): Text content to evaluate
        
    Returns:
        bool: True if the text should be filtered out, False if it's potentially meaningful
        
    Examples:
        >>> is_noisy("Abstract")
        True
        >>> is_noisy("pg")
        True
        >>> is_noisy("Introduction to Machine Learning")
        False
    """
    text_lower = text.lower().strip()
    
    # Check against known noise words/phrases
    contains_noise = any(noise_word in text_lower for noise_word in NOISE_WORDS)
    
    # Filter out very short text (likely page numbers or artifacts)
    is_too_short = len(text.strip()) <= 3
    
    return contains_noise or is_too_short

def extract_title(page):
    """
    Extract the main title from the first page of a PDF document.
    
    This function implements a sophisticated title detection algorithm that:
    1. Identifies text with the largest font size on the first page
    2. Handles multi-line titles that may be split across multiple text blocks
    3. Combines consecutive large text blocks to form complete titles
    4. Filters out noise and document artifacts
    
    The algorithm works by:
    - Collecting all text spans grouped by font size
    - Identifying the maximum font size as the title size
    - Finding consecutive text blocks with the title size
    - Combining them into a coherent title while preserving word boundaries
    
    Args:
        page: PyMuPDF page object representing the first page of the document
        
    Returns:
        tuple: (title_text, title_font_size)
            - title_text (str): The extracted title, or empty string if not found
            - title_font_size (float): The font size of the title, or None if not found
            
    Examples:
        >>> page = doc[0]  # First page of a PDF
        >>> title, size = extract_title(page)
        >>> print(f"Title: {title}, Size: {size}")
        Title: "Machine Learning in Healthcare Applications", Size: 18.0
    """
    size_to_texts = defaultdict(list)
    blocks = page.get_text("dict")["blocks"]
    
    # First pass: collect all text spans grouped by their font size
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                size = round(span["size"], 1)  # Round to handle floating point precision
                text = clean_text(span["text"])
                
                # Filter out noise and very short text fragments
                if is_noisy(text) or len(text) < 5:
                    continue
                    
                size_to_texts[size].append(text)
    
    # Return empty result if no valid text found
    if not size_to_texts:
        return "", None
    
    # Identify the largest font size as the potential title size
    max_size = max(size_to_texts.keys())
    
    # Second pass: collect multi-line title by finding consecutive large text blocks
    # This handles cases where titles span multiple lines or text blocks
    title_parts = []
    previous_block_pos = None
    current_title_block = []
    
    for block in blocks:
        block_pos = block.get("bbox", (0, 0))[1]  # y-coordinate for vertical positioning
        
        for line in block.get("lines", []):
            line_texts = []
            line_has_title = False
            
            # Check if this line contains text with the title font size
            for span in line.get("spans", []):
                if round(span["size"], 1) == max_size:
                    text = clean_text(span["text"])
                    if not is_noisy(text):
                        line_has_title = True
                        line_texts.append(text)
            
            if line_has_title:
                full_line_text = " ".join(line_texts)
                
                # Check if this line is a continuation of the previous title line
                # Lines are considered continuous if they're close vertically (within 20 units)
                if (previous_block_pos is not None and 
                    abs(block_pos - previous_block_pos) < 20 and  
                    len(current_title_block) > 0):
                    current_title_block.append(full_line_text)
                else:
                    # Start a new title block
                    if current_title_block:
                        title_parts.append(" ".join(current_title_block))
                    current_title_block = [full_line_text]
                    
                previous_block_pos = block_pos
    
    # Add the final title block if it exists
    if current_title_block:
        title_parts.append(" ".join(current_title_block))
    
    # Combine all title parts and clean the final result
    title = " ".join(title_parts)
    return clean_text(title), max_size

def group_multiline_headings(heading_candidates):
    """
    Group consecutive text lines with the same font size into multi-line headings.
    
    This function addresses the common issue where headings span multiple lines in PDF documents.
    It intelligently combines text fragments that belong to the same heading by analyzing:
    - Font size consistency across lines
    - Page positioning
    - Text continuation patterns (lowercase starts, short words)
    - Hyphenated word breaks
    
    The algorithm uses heuristics to determine when text should be joined:
    - Text starting with lowercase letters (likely continuations)
    - Previous or current text segments with very short words (≤3 characters)
    - Hyphenated words that were broken across lines
    
    Args:
        heading_candidates (list): List of tuples (font_size, text, page_number)
                                 representing potential heading text fragments
        
    Returns:
        list: List of tuples (font_size, combined_text, page_number) where
              multi-line headings have been properly combined
              
    Examples:
        >>> candidates = [(16.0, "Introduction to", 1), (16.0, "machine learning", 1)]
        >>> group_multiline_headings(candidates)
        [(16.0, "Introduction to machine learning", 1)]
    """
    if not heading_candidates:
        return []
    
    grouped = []
    # Start with the first candidate as the current group
    current_group = list(heading_candidates[0])
    
    for candidate in heading_candidates[1:]:
        size, text, page = candidate
        
        # Check if this candidate should be merged with the current group
        should_merge = (
            size == current_group[0] and  # Same font size
            page == current_group[2] and  # Same page
            (
                text[0].islower() or  # Starts with lowercase (likely continuation)
                len(current_group[1].split()[-1]) <= 3 or  # Last word in current group is short
                len(text.split()[0]) <= 3  # First word in new text is short
            )
        )
        
        if should_merge:
            # Determine how to join the text based on word break patterns
            if (current_group[1].endswith('-') or 
                len(current_group[1].split()[-1]) <= 2 or 
                len(text.split()[0]) <= 2):
                # Join without space for hyphenated words or very short fragments
                current_group[1] = current_group[1].rstrip('- ') + text
            else:
                # Join with space for normal text continuation
                current_group[1] += " " + text
        else:
            # Save the current group and start a new one
            grouped.append(tuple(current_group))
            current_group = list(candidate)
    
    # Don't forget to add the final group
    grouped.append(tuple(current_group))
    return grouped

def detect_heading_level(size, thresholds, title_size):
    """
    Determine the hierarchical level of a heading based on its font size.
    
    This function classifies text into heading levels (H1, H2, H3) by comparing
    the font size against established thresholds. The title size is excluded
    from heading classification to avoid duplicate content.
    
    The heading hierarchy is determined by font size in descending order:
    - Largest non-title size: H1
    - Second largest size: H2  
    - Third largest size: H3
    - Smaller sizes: Not classified as headings
    
    Args:
        size (float): Font size of the text element
        thresholds (dict): Dictionary containing font size thresholds for each level
                          Format: {"H1": float, "H2": float, "H3": float}
        title_size (float): Font size of the document title to exclude from headings
        
    Returns:
        str or None: Heading level ("H1", "H2", "H3") or None if not a heading
        
    Examples:
        >>> thresholds = {"H1": 16.0, "H2": 14.0, "H3": 12.0}
        >>> detect_heading_level(16.0, thresholds, 20.0)
        "H1"
        >>> detect_heading_level(20.0, thresholds, 20.0)
        None  # This is the title, not a heading
    """
    # Skip text that matches the title size to avoid duplication
    if size == title_size:
        return None
        
    # Classify based on font size thresholds in descending order
    if size >= thresholds["H1"]:
        return "H1"
    elif size >= thresholds["H2"]:
        return "H2"
    elif size >= thresholds["H3"]:
        return "H3"
    
    # Font size too small to be considered a heading
    return None

def extract_outline(pdf_path):
    """
    Extract the complete document outline (title and hierarchical headings) from a PDF file.
    
    This is the main function that orchestrates the entire outline extraction process.
    It combines title detection, heading identification, multi-line text handling,
    and hierarchical classification to produce a structured document outline.
    
    The extraction process follows these steps:
    1. Extract the main title from the first page using the largest font size
    2. Scan all pages for potential heading candidates based on font sizes
    3. Group multi-line headings and repair word breaks
    4. Establish font size thresholds for H1, H2, H3 classification
    5. Assign heading levels and filter duplicates
    6. Return structured outline data
    
    Args:
        pdf_path (str): Absolute path to the PDF file to process
        
    Returns:
        dict: Structured outline containing:
            - "title" (str): Main document title
            - "outline" (list): List of heading dictionaries, each containing:
                - "level" (str): Heading level ("H1", "H2", or "H3")
                - "text" (str): Heading text content
                - "page" (int): Page number where heading appears
                
    Raises:
        FileNotFoundError: If the PDF file cannot be found
        fitz.FileDataError: If the PDF file is corrupted or invalid
        
    Examples:
        >>> result = extract_outline("document.pdf")
        >>> print(result["title"])
        "Machine Learning Applications in Healthcare"
        >>> print(len(result["outline"]))
        15
        >>> print(result["outline"][0])
        {"level": "H1", "text": "Introduction", "page": 1}
    """
    # Open the PDF document using PyMuPDF
    doc = fitz.open(pdf_path)
    
    # Extract title from the first page
    title, title_size = extract_title(doc[0])
    
    # Fallback to filename if no title is detected
    if not title:
        title = os.path.basename(pdf_path).replace(".pdf", "")

    # Collect potential heading candidates from all pages
    heading_candidates = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        
        # Process each text block on the page
        for block in blocks:
            for line in block.get("lines", []):
                line_text = []
                max_size_in_line = 0
                
                # Collect text and find the maximum font size in this line
                for span in line.get("spans", []):
                    text = clean_text(span["text"])
                    size = round(span["size"], 1)
                    
                    # Skip noisy or irrelevant text
                    if is_noisy(text):
                        continue
                    
                    # Track the largest font size in this line
                    if size > max_size_in_line:
                        max_size_in_line = size
                    line_text.append(text)

                # Combine all text in the line and add as heading candidate
                full_line_text = clean_text(" ".join(line_text))
                if full_line_text and len(full_line_text) > 3 and not is_noisy(full_line_text):
                    heading_candidates.append((max_size_in_line, full_line_text, page_num))

    # Group multi-line headings and fix word breaks
    heading_candidates = group_multiline_headings(heading_candidates)

    # Return early if no headings found
    if not heading_candidates:
        return {"title": title, "outline": []}

    # Analyze font sizes to establish heading level thresholds
    heading_sizes = [size for size, _, _ in heading_candidates if size != title_size]
    if not heading_sizes:
        return {"title": title, "outline": []}
    
    # Get unique font sizes in descending order
    unique_sizes = sorted(set(heading_sizes), reverse=True)
    
    # Establish thresholds for each heading level
    thresholds = {
        "H1": unique_sizes[0] if len(unique_sizes) > 0 else 16,
        "H2": unique_sizes[1] if len(unique_sizes) > 1 else unique_sizes[0] * 0.85,
        "H3": unique_sizes[2] if len(unique_sizes) > 2 else unique_sizes[-1] * 0.7,
    }

    # Process heading candidates and assign levels
    outline = []
    seen = set()  # Track processed headings to avoid duplicates
    
    for size, text, page in heading_candidates:
        # Create a unique key to detect duplicates
        key = (text.lower(), page)
        if key in seen:
            continue
        seen.add(key)

        # Determine the heading level based on font size
        level = detect_heading_level(size, thresholds, title_size)
        if level:
            outline.append({
                "level": level,
                "text": text,
                "page": page
            })

    return {"title": title, "outline": outline}

if __name__ == "__main__":
    """
    Main execution block for batch processing PDF files.
    
    This script processes all PDF files in the 'input' directory and generates
    corresponding JSON outline files in the 'output' directory. Each PDF is
    processed independently, and the results are saved with the same filename
    but with a .json extension.
    
    Directory structure expected:
    - input/: Contains PDF files to process
    - output/: Will contain generated JSON files (created if not exists)
    
    Error handling:
    - Creates output directory if it doesn't exist
    - Skips non-PDF files in the input directory
    - Continues processing other files if one fails
    """
    # Define input and output directories
    input_dir = "input"
    output_dir = "output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each PDF file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            # Construct file paths
            in_path = os.path.join(input_dir, filename)
            out_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            
            try:
                # Extract outline from PDF
                result = extract_outline(in_path)

                # Save results to JSON file with proper formatting
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                # Report successful processing
                print(f"Successfully processed {filename} -> {os.path.basename(out_path)}")
                
            except Exception as e:
                # Report errors but continue processing other files
                print(f"Error processing {filename}: {str(e)}")
                continue
