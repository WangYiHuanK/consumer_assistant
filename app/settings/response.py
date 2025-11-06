# Views package for handling presentation layer in FastAPI context
from typing import Dict, Any, Optional, List
from fastapi.responses import JSONResponse


def create_response(
    success: bool,
    code: int,
    message: str,
    data: Optional[Any] = None,
    pagination: Optional[Dict[str, Any]] = None,
    # 分页参数，可直接传入而无需先调用paginate_response
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    total: Optional[int] = None
) -> JSONResponse:
    """
    通用响应函数，支持直接传入分页参数或已构建的分页对象
    
    Args:
        success: 成功标志
        code: 响应码
        message: 响应消息
        data: 可选的数据负载（可为null）
        pagination: 可选的分页信息（可为null）
        page: 当前页码（如果提供，则自动计算分页信息）
        page_size: 每页大小（如果提供，则自动计算分页信息）
        total: 总记录数（如果提供，则自动计算分页信息）
        
    Returns:
        标准化格式的JSONResponse
    """
    # 如果提供了分页参数且没有提供pagination对象，则自动计算分页信息
    if pagination is None and all(param is not None for param in [page, page_size, total]):
        pagination = {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    response_data = {
        "success": success,
        "code": code,
        "message": message,
        "data": data,  # 始终存在，可为null
        "pagination": pagination  # 始终存在，可为null
    }
    
    return JSONResponse(content=response_data)


def paginate_response(
    page: int,
    page_size: int,
    total: int
) -> Dict[str, Any]:
    """
    创建分页元数据的辅助函数（保持向后兼容）
    
    Args:
        page: 当前页码
        page_size: 每页大小
        total: 总记录数
        
    Returns:
        包含分页元数据的字典
    """
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }


def success_response(
    message: str = "操作成功",
    data: Optional[Any] = None,
    pagination: Optional[Dict[str, Any]] = None,
    # 支持直接传入分页参数
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    total: Optional[int] = None
) -> JSONResponse:
    """
    成功响应辅助函数，支持直接传入分页参数
    
    Args:
        message: 响应消息
        data: 可选的数据负载
        pagination: 可选的分页信息
        page: 当前页码
        page_size: 每页大小
        total: 总记录数
        
    Returns:
        成功格式的JSONResponse
    """
    return create_response(
        success=True,
        code=200,
        message=message,
        data=data,
        pagination=pagination,
        page=page,
        page_size=page_size,
        total=total
    )


def error_response(
    code: int,
    message: str,
    data: Optional[Any] = None
) -> JSONResponse:
    """
    错误响应辅助函数
    
    Args:
        code: 错误码
        message: 错误消息
        data: 可选的错误数据
        
    Returns:
        错误格式的JSONResponse
    """
    return create_response(
        success=False,
        code=code,
        message=message,
        data=data,
        pagination=None
    )