"""Replicates the original Spring Data ``Page<T>`` JSON envelope so existing
frontend clients keep working unchanged: zero-indexed ``page``/``size`` query
params, and a response with ``content``, ``pageable``, ``totalElements``, etc.
"""

DEFAULT_PAGE_SIZE = 10


def _as_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def paginate_queryset(queryset, request):
    page = max(_as_int(request.query_params.get("page"), 0), 0)
    size = max(_as_int(request.query_params.get("size"), DEFAULT_PAGE_SIZE), 1)

    total_elements = queryset.count()
    offset = page * size
    content = list(queryset[offset : offset + size])

    return content, page, size, total_elements


def page_response(content_data, page: int, size: int, total_elements: int) -> dict:
    total_pages = -(-total_elements // size) if size > 0 else 0
    unsorted_sort = {"empty": True, "sorted": False, "unsorted": True}

    return {
        "content": content_data,
        "pageable": {
            "pageNumber": page,
            "pageSize": size,
            "offset": page * size,
            "sort": unsorted_sort,
            "paged": True,
            "unpaged": False,
        },
        "totalElements": total_elements,
        "totalPages": total_pages,
        "size": size,
        "number": page,
        "sort": unsorted_sort,
        "first": page == 0,
        "last": True if total_pages == 0 else (page + 1) >= total_pages,
        "numberOfElements": len(content_data),
        "empty": len(content_data) == 0,
    }
