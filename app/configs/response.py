# Views package for handling presentation layer in FastAPI context
from typing import Dict, Any, Optional, List
from fastapi.responses import JSONResponse


def create_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Helper function to create standardized API responses
    
    Args:
        success: Boolean indicating if the operation was successful
        message: Response message
        data: Optional data payload
        status_code: HTTP status code
        
    Returns:
        JSONResponse with standardized format
    """
    response_data = {
        "success": success,
        "message": message,
    }
    
    if data is not None:
        response_data["data"] = data
    
    return JSONResponse(
        content=response_data,
        status_code=status_code
    )


def paginate_response(
    items: List[Any],
    page: int,
    page_size: int,
    total: int
) -> Dict[str, Any]:
    """
    Helper function to format paginated responses
    
    Args:
        items: List of items for the current page
        page: Current page number
        page_size: Number of items per page
        total: Total number of items
        
    Returns:
        Dict with pagination metadata and items
    """
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }