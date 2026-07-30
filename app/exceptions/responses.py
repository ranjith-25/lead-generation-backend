from datetime import datetime

def error_response(
    message: str,
    code: str,
    status_code: int,
    details=None,
):
    return {
        "success": False,
        "status_code": status_code,
        "error_code": code,
        "message": message,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
