"""
Fuzzy Matcher for Drug Names
Provides fuzzy string matching for drug identification.
"""

import logging
from typing import List, Dict, Optional
from difflib import SequenceMatcher
import re

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """Service for fuzzy matching of drug names."""

    def __init__(self):
        self.drug_database = self._load_drug_database()

    def find_matches(self, query: str, threshold: float = 0.6) -> List[Dict]:
        """
        Find fuzzy matches for a drug name query.

        Args:
            query: The drug name to search for
            threshold: Minimum similarity score (0-1)

        Returns:
            List of matches with similarity scores
        """
        if not query or not query.strip():
            return []

        # Normalize query
        normalized_query = self._normalize_text(query.strip())

        matches = []

        for drug_name in self.drug_database:
            similarity = self._calculate_similarity(normalized_query, drug_name)

            if similarity >= threshold:
                matches.append({
                    "drug_name": drug_name,
                    "similarity": similarity,
                    "match_type": "fuzzy"
                })

        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x["similarity"], reverse=True)

        return matches[:10]  # Return top 10 matches

    def _calculate_similarity(self, query: str, target: str) -> float:
        """
        Calculate similarity between query and target strings.

        Uses multiple similarity metrics for better accuracy.
        """
        if not query or not target:
            return 0.0

        # SequenceMatcher similarity
        seq_similarity = SequenceMatcher(None, query.lower(), target.lower()).ratio()

        # Jaccard similarity for word sets
        query_words = set(query.lower().split())
        target_words = set(target.lower().split())

        if query_words and target_words:
            intersection = query_words.intersection(target_words)
            union = query_words.union(target_words)
            jaccard_similarity = len(intersection) / len(union)
        else:
            jaccard_similarity = 0.0

        # Weighted combination
        combined_similarity = (seq_similarity * 0.7) + (jaccard_similarity * 0.3)

        return combined_similarity

    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching."""
        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove common drug suffixes/prefixes that might cause mismatches
        text = re.sub(r'\s+(tablet|capsule|pill|mg|ml|units?|injection|syrup)\b', '', text)
        text = re.sub(r'\b(drug|medication|medicine)\s+', '', text)

        return text.strip()

    def _load_drug_database(self) -> List[str]:
        """Load the drug database for matching."""
        # In production, this would be loaded from a database or file
        # For now, using a comprehensive list of common drugs
        return [
            "hydrochlorothiazide",
            "lisinopril",
            "metformin",
            "simvastatin",
            "omeprazole",
            "amoxicillin",
            "azithromycin",
            "prednisone",
            "warfarin",
            "digoxin",
            "furosemide",
            "spironolactone",
            "metoprolol",
            "atenolol",
            "amlodipine",
            "losartan",
            "gabapentin",
            "sertraline",
            "citalopram",
            "escitalopram",
            "fluoxetine",
            "paroxetine",
            "trazodone",
            "bupropion",
            "venlafaxine",
            "duloxetine",
            "clonazepam",
            "lorazepam",
            "alprazolam",
            "diazepam",
            "zolpidem",
            "tramadol",
            "oxycodone",
            "hydrocodone",
            "morphine",
            "fentanyl",
            "codeine",
            "ibuprofen",
            "naproxen",
            "acetaminophen",
            "aspirin",
            "celecoxib",
            "meloxicam",
            "diclofenac",
            "indomethacin",
            "allopurinol",
            "colchicine",
            "probenecid",
            "febuxostat",
            "levothyroxine",
            "liothyronine",
            "methimazole",
            "propylthiouracil",
            "glipizide",
            "glyburide",
            "glimepiride",
            "pioglitazone",
            "rosiglitazone",
            "sitagliptin",
            "linagliptin",
            "saxagliptin",
            "empagliflozin",
            "dapagliflozin",
            "canagliflozin",
            "insulin glargine",
            "insulin lispro",
            "insulin aspart",
            "insulin detemir",
            "exenatide",
            "liraglutide",
            "semaglutide",
            "dulaglutide",
            "albuterol",
            "salmeterol",
            "fluticasone",
            "budesonide",
            "montelukast",
            "zafirlukast",
            "omalizumab",
            "mepolizumab",
            "reslizumab",
            "benzonatate",
            "guaifenesin",
            "dextromethorphan",
            "diphenhydramine",
            "loratadine",
            "cetirizine",
            "fexofenadine",
            "desloratadine",
            "levocetirizine",
            "ranitidine",
            "famotidine",
            "cimetidine",
            "esomeprazole",
            "lansoprazole",
            "dexlansoprazole",
            "pantoprazole",
            "rabeprazole",
            "sucralfate",
            "misoprostol",
            "metoclopramide",
            "ondansetron",
            "promethazine",
            "prochlorperazine",
            "dimenhydrinate",
            "meclizine",
            "scopolamine",
            "dicyclomine",
            "hyoscyamine",
            "loperamide",
            "bismuth subsalicylate",
            "kaolin-pectin",
            "attapulgite",
            "aluminum hydroxide",
            "magnesium hydroxide",
            "calcium carbonate",
            "famotidine-calcium carbonate",
            "cimetidine",
            "nizatidine",
            "lansoprazole",
            "dexlansoprazole",
            "esomeprazole",
            "omeprazole",
            "pantoprazole",
            "rabeprazole",
            "sucralfate",
            "misoprostol"
        ]

    def find_best_match(self, query: str) -> Optional[Dict]:
        """
        Find the best fuzzy match for a query.

        Args:
            query: The drug name to search for

        Returns:
            Best match dictionary or None
        """
        matches = self.find_matches(query, threshold=0.3)  # Lower threshold for best match

        if matches:
            return matches[0]

        return None

    def get_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Get drug name suggestions based on partial input.

        Args:
            partial_query: Partial drug name
            limit: Maximum number of suggestions

        Returns:
            List of suggested drug names
        """
        if not partial_query or len(partial_query) < 2:
            return []

        matches = self.find_matches(partial_query, threshold=0.4)

        # Filter to drugs that start with the partial query
        suggestions = []
        partial_lower = partial_query.lower()

        for match in matches:
            if match["drug_name"].lower().startswith(partial_lower):
                suggestions.append(match["drug_name"])
                if len(suggestions) >= limit:
                    break

        return suggestions
