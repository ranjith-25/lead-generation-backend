from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class CommentNotFoundException(AppException):
    """Raised for a comment id that does not exist and for one that is already soft-deleted —
    a removed comment must not be editable through a stale id the client still holds."""

    def __init__(self):
        super().__init__(
            message="Comment not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.COMMENT_NOT_FOUND,
        )


class CommentEditNotAllowedException(AppException):
    """Editing and deleting are author-only, regardless of role: a comment is a statement
    someone made, so no permission level lets another user rewrite it in their name."""

    def __init__(self):
        super().__init__(
            message="Only the author can edit or delete this comment",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.COMMENT_EDIT_NOT_ALLOWED,
        )


class CommentEntityNotFoundException(AppException):
    """The (page_name, entity_id) pair addresses no row. `entity_id` carries no foreign key —
    it points at one of three tables — so this is the check that would otherwise be one."""

    def __init__(self):
        super().__init__(
            message="The record this comment belongs to was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.COMMENT_ENTITY_NOT_FOUND,
        )
