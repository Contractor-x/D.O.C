"""
Content ranking and relevance scoring for research articles.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class ContentRanker:
    """Ranks and scores research content for relevance."""

    def __init__(self):
        """Initialize content ranker."""
        self.relevance_weights = {
            'title_match': 0.3,
            'abstract_match': 0.25,
            'recency': 0.2,
            'source_authority': 0.15,
            'clinical_relevance': 0.1
        }

    def rank_articles(self, articles: List[Dict[str, Any]], query: str, illness_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Rank articles by relevance to query and illness type.

        Args:
            articles: List of article dictionaries
            query: Search query
            illness_type: Type of illness (e.g., "cancer", "diabetes")

        Returns:
            Ranked list of articles with scores
        """
        ranked_articles = []

        for article in articles:
            if 'error' in article:
                # Skip error entries
                continue

            score = self._calculate_relevance_score(article, query, illness_type)
            article_with_score = article.copy()
            article_with_score['relevance_score'] = score
            ranked_articles.append(article_with_score)

        # Sort by relevance score (descending)
        ranked_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return ranked_articles

    def _calculate_relevance_score(self, article: Dict[str, Any], query: str, illness_type: Optional[str] = None) -> float:
        """Calculate relevance score for an article."""
        score = 0.0

        # Title matching
        title_score = self._calculate_text_match_score(article.get('title', ''), query)
        score += title_score * self.relevance_weights['title_match']

        # Abstract matching
        abstract_score = self._calculate_text_match_score(article.get('abstract', ''), query)
        score += abstract_score * self.relevance_weights['abstract_match']

        # Recency score
        recency_score = self._calculate_recency_score(article.get('publication_date'))
        score += recency_score * self.relevance_weights['recency']

        # Source authority
        authority_score = self._calculate_authority_score(article.get('source', ''))
        score += authority_score * self.relevance_weights['source_authority']

        # Clinical relevance
        clinical_score = self._calculate_clinical_relevance(article, illness_type)
        score += clinical_score * self.relevance_weights['clinical_relevance']

        return round(score, 3)

    def _calculate_text_match_score(self, text: str, query: str) -> float:
        """Calculate how well text matches the query."""
        if not text or not query:
            return 0.0

        text_lower = text.lower()
        query_lower = query.lower()

        # Exact phrase match
        if query_lower in text_lower:
            return 1.0

        # Word-by-word matching
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        text_words = set(re.findall(r'\b\w+\b', text_lower))

        if not query_words:
            return 0.0

        matching_words = query_words.intersection(text_words)
        match_ratio = len(matching_words) / len(query_words)

        return min(match_ratio, 1.0)

    def _calculate_recency_score(self, pub_date_str: Optional[str]) -> float:
        """Calculate recency score based on publication date."""
        if not pub_date_str:
            return 0.0

        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    pub_date = datetime.strptime(pub_date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return 0.0

            days_since_publication = (datetime.now() - pub_date).days

            # Exponential decay: newer articles get higher scores
            if days_since_publication <= 0:
                return 1.0
            elif days_since_publication <= 7:
                return 0.9
            elif days_since_publication <= 30:
                return 0.7
            elif days_since_publication <= 90:
                return 0.5
            elif days_since_publication <= 365:
                return 0.3
            else:
                return 0.1

        except Exception:
            return 0.0

    def _calculate_authority_score(self, source: str) -> float:
        """Calculate authority score based on source."""
        if not source:
            return 0.0

        source_lower = source.lower()

        # High authority sources
        if 'pubmed' in source_lower or 'nih' in source_lower:
            return 1.0
        elif 'clinicaltrials.gov' in source_lower:
            return 0.9
        elif 'fda' in source_lower or 'who' in source_lower:
            return 0.8
        elif 'medline' in source_lower or 'cochrane' in source_lower:
            return 0.7
        elif 'nejm' in source_lower or 'jama' in source_lower or 'lancet' in source_lower:
            return 0.8
        else:
            return 0.5

    def _calculate_clinical_relevance(self, article: Dict[str, Any], illness_type: Optional[str]) -> float:
        """Calculate clinical relevance score."""
        if not illness_type:
            return 0.5  # Neutral score if no illness specified

        text_to_check = (article.get('title', '') + ' ' + article.get('abstract', '')).lower()
        illness_lower = illness_type.lower()

        # Check for illness mentions
        if illness_lower in text_to_check:
            return 0.9

        # Check for related terms
        related_terms = self._get_related_terms(illness_type)
        matching_terms = [term for term in related_terms if term in text_to_check]

        if matching_terms:
            return min(0.8, len(matching_terms) * 0.2)

        return 0.1

    def _get_related_terms(self, illness_type: str) -> List[str]:
        """Get related medical terms for an illness type."""
        illness_terms = {
            'cancer': ['tumor', 'carcinoma', 'malignant', 'chemotherapy', 'radiation', 'oncology'],
            'diabetes': ['insulin', 'glucose', 'blood sugar', 'hyperglycemia', 'diabetic'],
            'heart disease': ['cardiovascular', 'coronary', 'myocardial', 'cholesterol', 'hypertension'],
            'depression': ['mental health', 'anxiety', 'mood', 'antidepressant', 'therapy'],
            'asthma': ['respiratory', 'bronchodilator', 'inhaler', 'allergy'],
            'arthritis': ['joint', 'inflammation', 'rheumatoid', 'osteoarthritis', 'pain'],
            'alzheimer': ['dementia', 'cognitive', 'memory', 'neurological'],
            'parkinson': ['tremor', 'movement', 'dopamine', 'neurological']
        }

        return illness_terms.get(illness_type.lower(), [])

    def filter_by_relevance_threshold(self, articles: List[Dict[str, Any]], threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Filter articles by minimum relevance score.

        Args:
            articles: List of articles with relevance scores
            threshold: Minimum relevance score

        Returns:
            Filtered list of articles
        """
        return [article for article in articles if article.get('relevance_score', 0) >= threshold]

    def get_top_articles(self, articles: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N most relevant articles.

        Args:
            articles: List of articles with relevance scores
            top_n: Number of top articles to return

        Returns:
            Top N articles
        """
        sorted_articles = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        return sorted_articles[:top_n]
