"""
API client utilities for external service integrations.
"""

import requests
import time
from typing import Dict, Any, Optional
from functools import wraps


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry API calls on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        raise last_exception
            return None
        return wrapper
    return decorator


class APIClient:
    """Base API client with common functionality."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize API client.

        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'User-Agent': 'DOC-Medication-Platform/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    @retry_on_failure(max_retries=3, delay=1.0)
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

    @retry_on_failure(max_retries=3, delay=1.0)
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make POST request.

        Args:
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

    def set_auth_header(self, header_name: str, header_value: str):
        """Set custom authentication header."""
        self.session.headers.update({header_name: header_value})

    def add_header(self, name: str, value: str):
        """Add custom header."""
        self.session.headers.update({name: value})


class OpenFDAClient(APIClient):
    """Client for OpenFDA API."""

    def __init__(self):
        super().__init__("https://api.fda.gov")

    def search_drug_info(self, drug_name: str) -> Dict[str, Any]:
        """
        Search for drug information.

        Args:
            drug_name: Name of the drug

        Returns:
            Drug information
        """
        endpoint = "/drug/label.json"
        params = {
            "search": f"openfda.brand_name:{drug_name}",
            "limit": 1
        }

        return self.get(endpoint, params)

    def get_drug_adverse_events(self, drug_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get adverse events for a drug.

        Args:
            drug_name: Name of the drug
            limit: Maximum results

        Returns:
            Adverse events data
        """
        endpoint = "/drug/event.json"
        params = {
            "search": f"patient.drug.medicinalproduct:{drug_name}",
            "count": "patient.reaction.reactionmeddrapt.exact",
            "limit": limit
        }

        return self.get(endpoint, params)


class PubMedClient(APIClient):
    """Client for PubMed E-utilities API."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
        self.api_key = api_key

    def search_articles(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search PubMed articles.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            Search results
        """
        endpoint = "/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }

        if self.api_key:
            params["api_key"] = self.api_key

        return self.get(endpoint, params)

    def fetch_article_details(self, article_ids: list) -> Dict[str, Any]:
        """
        Fetch detailed article information.

        Args:
            article_ids: List of PubMed IDs

        Returns:
            Article details
        """
        endpoint = "/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(article_ids),
            "retmode": "xml"
        }

        if self.api_key:
            params["api_key"] = self.api_key

        # This returns XML, not JSON
        response = self.session.get(f"{self.base_url}/{endpoint.lstrip('/')}", params=params, timeout=self.timeout)
        return {"xml_content": response.text, "status_code": response.status_code}
