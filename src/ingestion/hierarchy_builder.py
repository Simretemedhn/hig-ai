"""
src/ingestion/hierarchy_builder.py

Module for transforming raw page text into structured legal JSON hierarchies 
(Proclamation -> Chapter -> Article -> Sub-article) using Regular Expressions.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any


class LegalHierarchyBuilder:
    """Parses raw legal text and structures it into hierarchical JSON objects."""

    def __init__(self, raw_pages: List[Dict[str, Any]], proclamation_title: str):
        self.raw_pages = raw_pages
        self.proclamation_title = proclamation_title

    def consolidate_text(self) -> str:
        """Joins all page text into a single continuous string for pattern matching."""
        full_text = "\n".join([page["text"] for page in self.raw_pages])
        return full_text

    def parse_articles(self) -> List[Dict[str, Any]]:
        """
        Uses Regular Expressions to split raw legal text into individual Articles.
        
        Ethiopian Federal Proclamations typically follow patterns like:
        'Article 5.' or '5. Subject Title'
        """
        full_text = self.consolidate_text()

        # Regex pattern to match "Article <Number>" followed by optional dot/spaces and a title
        # r"" means raw string in Python so backslashes are treated literally.
        article_pattern = re.compile(r"(?:Article|አንቀጽ)\s+(\d+)\s*\n*\s*(.*?)(?=(?:Article|አንቀጽ)\s+\d+|\Z)", re.DOTALL)
        
        matches = article_pattern.findall(full_text)
        structured_articles = []

        for match in matches:
            article_number = match[0]
            article_body = match[1].strip()

            # Clean up excessive newlines inside the article body
            cleaned_body = re.sub(r'\n+', ' ', article_body)

            structured_articles.append({
                "proclamation": self.proclamation_title,
                "article_number": int(article_number),
                "title_and_content": cleaned_body,
                "status": "ACTIVE", # Default metadata tag for versioning
            })

        return structured_articles

    def save_to_json(self, output_path: str) -> None:
        """Saves the structured legal hierarchy into a clean JSON file."""
        articles = self.parse_articles()
        output_file = Path(output_path)
        
        # Ensure parent directories exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
            
        print(f"[Success] Saved {len(articles)} structured articles to {output_file}")


if __name__ == "__main__":
    # Test simulation with mock data if no PDF is parsed yet
    mock_pages = [
        {
            "page_number": 1,
            "text": "Federal Negarit Gazette\nArticle 1. Short Title\nThis Proclamation may be cited as the 'Commercial Code of Ethiopia 2021'.\n\nArticle 2. Definitions\nIn this Proclamation, unless the context requires otherwise..."
        }
    ]

    print("--- Running Hierarchy Builder Test ---")
    builder = LegalHierarchyBuilder(mock_pages, proclamation_title="Commercial Code Proclamation No. 1243/2021")
    articles = builder.parse_articles()
    
    print(f"Extracted {len(articles)} structured articles.")
    for art in articles:
        print(f"\n-> Article {art['article_number']}:\n{art['title_and_content'][:150]}...")