from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class InvalidSalesEnablementIdException(AppException):

    def __init__(self, sales_enablement_id=None):
        super().__init__(
            message="Invalid Sales Enablement ID format",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVALID_SALES_ENABLEMENT_ID,
            details={"salesEnablementID": str(sales_enablement_id)} if sales_enablement_id else None,
        )


class SalesEnablementNotFoundException(AppException):

    def __init__(self, sales_enablement_id=None):
        super().__init__(
            message="Sales Enablement not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.SALES_ENABLEMENT_NOT_FOUND,
            details={"salesEnablementID": str(sales_enablement_id)} if sales_enablement_id else None,
        )

class SalesEnablementAlreadyExistsException(AppException):

    def __init__(self, opportunity_id=None):
        super().__init__(
            message="Sales Enablement already exists for this opportunity",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.SALES_ENABLEMENT_ALREADY_EXISTS,
            details={"opportunityID": str(opportunity_id)} if opportunity_id else None,
        )
