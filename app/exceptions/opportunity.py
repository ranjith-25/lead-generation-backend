from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class InvalidOpportunityIdException(AppException):

    def __init__(self, opportunity_id=None):
        super().__init__(
            message="Invalid Opportunity ID format",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVALID_OPPORTUNITY_ID,
            details={"opportunityID": str(opportunity_id)} if opportunity_id else None,
        )


class OpportunityNotFoundException(AppException):

    def __init__(self, opportunity_id=None):
        super().__init__(
            message="Opportunity not found or unauthorized",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.OPPORTUNITY_NOT_FOUND,
            details={"opportunityID": str(opportunity_id)} if opportunity_id else None,
        )
