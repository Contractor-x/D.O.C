"""
NDC Lookup Service
Provides NDC (National Drug Code) lookup functionality.
"""

import logging
import re
from typing import Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class NDCLookup:
    """Service for NDC code lookups and drug identification."""

    def __init__(self):
        self.base_url = "https://api.fda.gov/drug/ndc.json"
        self.ndc_pattern = re.compile(r'^(\d{4,5})-(\d{3,4})-(\d{1,2})$')

        # Local cache for common NDCs (in production, use Redis/database)
        self._cache = {}

    async def lookup_by_ndc(self, ndc_code: str) -> Dict:
        """
        Lookup drug information by NDC code.

        Args:
            ndc_code: NDC code (with or without dashes)

        Returns:
            Dict containing drug information
        """
        try:
            # Normalize NDC format
            normalized_ndc = self._normalize_ndc(ndc_code)

            if not normalized_ndc:
                return {
                    "found": False,
                    "error": "Invalid NDC format"
                }

            # Check cache first
            if normalized_ndc in self._cache:
                return self._cache[normalized_ndc]

            # Query FDA API
            result = await self._query_fda_api(normalized_ndc)

            # Cache result
            self._cache[normalized_ndc] = result

            return result

        except Exception as e:
            logger.error(f"NDC lookup failed for {ndc_code}: {e}")
            return {
                "found": False,
                "error": str(e)
            }

    def _normalize_ndc(self, ndc: str) -> Optional[str]:
        """
        Normalize NDC code to standard format.

        Args:
            ndc: NDC code (various formats accepted)

        Returns:
            Normalized NDC string or None if invalid
        """
        if not ndc:
            return None

        # Remove all non-digits
        digits_only = re.sub(r'\D', '', ndc)

        # NDC should be 10 or 11 digits
        if len(digits_only) not in [10, 11]:
            return None

        # Format as XXX-XX-XXXX or XXXXX-XXXX-XX
        if len(digits_only) == 10:
            # 4-4-2 format
            return f"{digits_only[:4]}-{digits_only[4:8]}-{digits_only[8:]}"
        else:
            # 5-4-2 format
            return f"{digits_only[:5]}-{digits_only[5:9]}-{digits_only[9:]}"

    async def _query_fda_api(self, ndc: str) -> Dict:
        """
        Query FDA NDC API for drug information.

        Args:
            ndc: Normalized NDC code

        Returns:
            Dict with drug information
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "search": f"product_ndc:{ndc}",
                    "limit": 1
                }

                response = await client.get(self.base_url, params=params)
                response.raise_for_status()

                data = response.json()

                if data.get("results") and len(data["results"]) > 0:
                    drug_data = data["results"][0]

                    return {
                        "found": True,
                        "ndc": ndc,
                        "drug_name": drug_data.get("generic_name", drug_data.get("brand_name", "Unknown")),
                        "brand_name": drug_data.get("brand_name"),
                        "generic_name": drug_data.get("generic_name"),
                        "dosage_form": drug_data.get("dosage_form"),
                        "route": drug_data.get("route", []),
                        "strength": drug_data.get("active_ingredients", [{}])[0].get("strength", ""),
                        "manufacturer": drug_data.get("labeler_name"),
                        "product_type": drug_data.get("product_type"),
                        "marketing_status": drug_data.get("marketing_status"),
                        "source": "FDA_NDC_API"
                    }
                else:
                    return {
                        "found": False,
                        "ndc": ndc,
                        "error": "NDC not found in FDA database"
                    }

        except httpx.TimeoutException:
            logger.error(f"Timeout querying FDA API for NDC {ndc}")
            return {
                "found": False,
                "ndc": ndc,
                "error": "API timeout"
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error querying FDA API for NDC {ndc}: {e}")
            return {
                "found": False,
                "ndc": ndc,
                "error": f"API error: {e.response.status_code}"
            }

        except Exception as e:
            logger.error(f"Unexpected error querying FDA API for NDC {ndc}: {e}")
            return {
                "found": False,
                "ndc": ndc,
                "error": str(e)
            }

    def validate_ndc_format(self, ndc: str) -> bool:
        """
        Validate NDC code format.

        Args:
            ndc: NDC code to validate

        Returns:
            True if valid format
        """
        normalized = self._normalize_ndc(ndc)
        return normalized is not None

    def extract_ndc_from_text(self, text: str) -> Optional[str]:
        """
        Extract NDC code from text using regex patterns.

        Args:
            text: Text containing potential NDC code

        Returns:
            Extracted NDC code or None
        """
        # Pattern for NDC with dashes
        dash_pattern = r'\b\d{4,5}-\d{3,4}-\d{1,2}\b'
        match = re.search(dash_pattern, text)

        if match:
            return match.group()

        # Pattern for NDC without dashes (10-11 digits)
        no_dash_pattern = r'\b\d{10,11}\b'
        match = re.search(no_dash_pattern, text)

        if match:
            digits = match.group()
            return self._normalize_ndc(digits)

        return None

    async def batch_lookup(self, ndc_codes: list) -> Dict[str, Dict]:
        """
        Lookup multiple NDC codes in batch.

        Args:
            ndc_codes: List of NDC codes

        Returns:
            Dict mapping NDC codes to results
        """
        results = {}

        # Process in batches to avoid overwhelming the API
        batch_size = 10

        for i in range(0, len(ndc_codes), batch_size):
            batch = ndc_codes[i:i + batch_size]

            # Create tasks for concurrent requests
            import asyncio
            tasks = [self.lookup_by_ndc(ndc) for ndc in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for ndc, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    results[ndc] = {
                        "found": False,
                        "error": str(result)
                    }
                else:
                    results[ndc] = result

            # Small delay between batches to be respectful to the API
            if i + batch_size < len(ndc_codes):
                await asyncio.sleep(0.1)

        return results

    def get_ndc_components(self, ndc: str) -> Optional[Dict]:
        """
        Break down NDC into its components.

        Args:
            ndc: NDC code

        Returns:
            Dict with labeler, product, package codes
        """
        normalized = self._normalize_ndc(ndc)

        if not normalized:
            return None

        match = self.ndc_pattern.match(normalized)

        if match:
            return {
                "labeler_code": match.group(1),
                "product_code": match.group(2),
                "package_code": match.group(3),
                "formatted_ndc": normalized
            }

        return None
