from enum import Enum

class InvitationStatus(str, Enum):
    PENDING = "pending" #Invitation has been created and is waiting for the user to register.
    REGISTERED = "registered" #User has successfully completed registration.
    CANCELLED = "cancelled" #Invitation has been cancelled by an administrator.
    