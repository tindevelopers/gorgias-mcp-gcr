"""API client for Gorgias API."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
import httpx
from .auth import GorgiasAuth

logger = logging.getLogger(__name__)


class GorgiasAPIClient:
    """Client for interacting with Gorgias API."""
    
    def __init__(self, auth: GorgiasAuth, timeout: int = 30):
        """Initialize the API client.
        
        Args:
            auth: GorgiasAuth instance for authentication.
            timeout: Request timeout in seconds.
        """
        self.auth = auth
        self.timeout = timeout
        self.base_url = auth.get_base_url()
        self.headers = auth.get_headers()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Gorgias API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint (without base URL).
            params: Query parameters.
            data: Request body data.
            timeout: Request timeout override.
            
        Returns:
            JSON response data.
            
        Raises:
            httpx.HTTPError: If the request fails.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = timeout or self.timeout
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data
                )
                response.raise_for_status()
                if response.status_code == 204 or not response.content:
                    return {"status_code": response.status_code}

                try:
                    return response.json()
                except ValueError:
                    logger.warning(
                        "Received non-JSON response from %s %s", method, url
                    )
                    return {
                        "status_code": response.status_code,
                        "content": response.text
                    }
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                raise
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request.
        
        Args:
            endpoint: API endpoint.
            params: Query parameters.
            
        Returns:
            JSON response data.
        """
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request.
        
        Args:
            endpoint: API endpoint.
            data: Request body data.
            
        Returns:
            JSON response data.
        """
        return await self._make_request("POST", endpoint, data=data)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request.
        
        Args:
            endpoint: API endpoint.
            data: Request body data.
            
        Returns:
            JSON response data.
        """
        return await self._make_request("PUT", endpoint, data=data)
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PATCH request.
        
        Args:
            endpoint: API endpoint.
            data: Request body data.
            
        Returns:
            JSON response data.
        """
        return await self._make_request("PATCH", endpoint, data=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request.
        
        Args:
            endpoint: API endpoint.
            
        Returns:
            JSON response data.
        """
        return await self._make_request("DELETE", endpoint)
    
    async def get_paginated(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get paginated results from an endpoint.
        
        Args:
            endpoint: API endpoint.
            params: Query parameters.
            limit: Number of items per page.
            max_pages: Maximum number of pages to fetch (None for all).
            
        Returns:
            List of all items from all pages.
        """
        all_items = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
                
            paginated_params = (params or {}).copy()
            paginated_params.update({
                "limit": limit,
                "page": page
            })
            
            try:
                response = await self.get(endpoint, params=paginated_params)
                items = response.get("data", [])
                
                if not items:
                    break
                    
                all_items.extend(items)
                
                # Check if there are more pages
                if len(items) < limit:
                    break
                    
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        return all_items


