from pydantic import Field

from app.responses.base import BaseResponse


class RepairReportingHierarchyResponse(BaseResponse):
    scanned: int = Field(default=0, description="Live users found pointing at a deleted or missing manager")
    repaired: int = Field(default=0, description="Of those, the users re-pointed at their nearest live ancestor")
    orphaned: int = Field(default=0, description="Of those, the users whose reporting_to was cleared because no live ancestor exists")
    benched: int = Field(default=0, description="Users moved to the bench status because they hold no project allocations")
