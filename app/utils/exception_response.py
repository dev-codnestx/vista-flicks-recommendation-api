from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Custom exception handler for validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    
    # Extract and format error messages
    for error in exc.errors():
        error_messages.append({
            "msg": error["msg"],
            "type": error["type"]
        })
        
    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "message": "value is not a valid email address",
        }
    )
