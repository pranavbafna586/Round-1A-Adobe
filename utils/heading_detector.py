"""
Heading Detection Module

This module provides functions for detecting and classifying document headings
based on font size analysis. It implements a hierarchical approach to identify
titles and heading levels (H1, H2, H3) from extracted PDF text elements.

The module uses font size as the primary indicator of heading importance,
with larger fonts typically representing higher-level headings in document
structure conventions.

Author: Adobe Assessment Project
Date: 2025
"""


def detect_headings(elements):
    """
    Detect and classify headings from a list of text elements using font size analysis.
    
    This function implements a font-size-based heading detection algorithm that:
    1. Sorts all text elements by font size in descending order
    2. Identifies unique font sizes and maps them to heading levels
    3. Classifies the largest font as title, and subsequent sizes as H1, H2, H3
    4. Groups headings by their classification level
    
    The classification hierarchy follows this logic:
    - Largest font size: Document title
    - Second largest: H1 headings
    - Third largest: H2 headings  
    - Fourth largest: H3 headings
    - Smaller sizes: Not classified as headings
    
    Args:
        elements (list): List of text element dictionaries, each containing:
            - "text" (str): Text content
            - "size" (float): Font size
            - "page" (int): Page number
            - Additional metadata (font, etc.)
            
    Returns:
        dict: Structured outline containing:
            - "title" (str or None): Document title text
            - "h1" (list): List of H1 heading dictionaries
            - "h2" (list): List of H2 heading dictionaries  
            - "h3" (list): List of H3 heading dictionaries
            
            Each heading dictionary contains:
            - "text" (str): Heading text content
            - "page" (int): Page number where heading appears
            
    Examples:
        >>> elements = [
        ...     {"text": "Document Title", "size": 20.0, "page": 1},
        ...     {"text": "Chapter 1", "size": 16.0, "page": 1},
        ...     {"text": "Section 1.1", "size": 14.0, "page": 2}
        ... ]
        >>> result = detect_headings(elements)
        >>> print(result["title"])
        "Document Title"
        >>> print(len(result["h1"]))
        1
        
    Note:
        - Only the first occurrence of the largest font size is used as title
        - Multiple headings of the same level are collected in lists
        - Empty input returns an outline with None title and empty heading lists
    """
    # Sort elements by font size in descending order to establish hierarchy
    sorted_elements = sorted(elements, key=lambda x: -x["size"])
    
    # Extract all font sizes and get unique values in descending order
    sizes = [el["size"] for el in sorted_elements]
    unique_sizes = sorted(set(sizes), reverse=True)

    # Map font sizes to heading levels based on hierarchy
    size_to_level = {}
    if unique_sizes:
        size_to_level[unique_sizes[0]] = "title"
        if len(unique_sizes) > 1:
            size_to_level[unique_sizes[1]] = "h1"
        if len(unique_sizes) > 2:
            size_to_level[unique_sizes[2]] = "h2"
        if len(unique_sizes) > 3:
            size_to_level[unique_sizes[3]] = "h3"

    # Initialize the outline structure
    outline = {
        "title": None,
        "h1": [],
        "h2": [],
        "h3": []
    }

    # Process each element and classify it according to its font size
    for el in elements:
        level = size_to_level.get(el["size"])
        
        if level:
            if level == "title" and not outline["title"]:
                # Only take the first title occurrence
                outline["title"] = el["text"]
            elif level in ["h1", "h2", "h3"]:
                # Add heading to appropriate level list
                outline[level].append({
                    "text": el["text"],
                    "page": el["page"]
                })

    return outline
