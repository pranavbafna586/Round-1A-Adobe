"""
PDF Utilities Module

This module provides utility functions for extracting text elements from PDF files
using PyMuPDF (fitz). It handles the low-level PDF parsing operations and text
extraction that are used by the main outline extraction algorithm.

The module focuses on extracting text spans with their associated metadata
(font size, font family, page location) which is essential for document
structure analysis.

Author: Adobe Assessment Project
Date: 2025
"""

import fitz  # PyMuPDF library for PDF processing


def extract_pdf_elements(pdf_path):
    """
    Extract all text elements from a PDF file with their formatting metadata.
    
    This function performs comprehensive text extraction from a PDF document,
    capturing not only the text content but also crucial formatting information
    such as font size and font family. This metadata is essential for document
    structure analysis and heading detection.
    
    The extraction process:
    1. Opens the PDF document using PyMuPDF
    2. Iterates through all pages in the document
    3. Processes each text block and line on every page
    4. Extracts individual text spans with their formatting properties
    5. Returns a comprehensive list of all text elements
    
    Args:
        pdf_path (str): Absolute path to the PDF file to process
        
    Returns:
        list: List of dictionaries, each representing a text element with:
            - "text" (str): The actual text content
            - "size" (float): Font size of the text
            - "font" (str): Font family name
            - "page" (int): Page number where the text appears (1-indexed)
            
    Raises:
        FileNotFoundError: If the PDF file cannot be found at the specified path
        fitz.FileDataError: If the PDF file is corrupted or invalid
        
    Examples:
        >>> elements = extract_pdf_elements("document.pdf")
        >>> print(len(elements))
        245
        >>> print(elements[0])
        {"text": "Introduction", "size": 16.0, "font": "Arial-Bold", "page": 1}
        
    Note:
        - Empty text spans are automatically filtered out
        - Text is stripped of leading/trailing whitespace
        - Page numbers start from 1 (not 0)
    """
    # Open the PDF document
    doc = fitz.open(pdf_path)
    elements = []

    # Process each page in the document
    for page_number, page in enumerate(doc, start=1):
        # Get text content structured as blocks, lines, and spans
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            # Skip blocks that don't contain text lines (e.g., images)
            if "lines" not in block:
                continue
                
            # Process each line in the text block
            for line in block["lines"]:
                # Process each text span in the line
                for span in line["spans"]:
                    text = span["text"].strip()
                    
                    # Only include non-empty text spans
                    if text:
                        elements.append({
                            "text": text,
                            "size": span["size"],
                            "font": span["font"],
                            "page": page_number
                        })
    
    # Close the document to free memory
    doc.close()
    return elements
