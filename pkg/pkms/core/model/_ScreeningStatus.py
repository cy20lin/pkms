from enum import Enum

class ScreeningStatus(str, Enum):
    # safe to ingest automatically
    APPROVED = "APPROVED" 
    # must not ingest
    REJECTED = "REJECTED"
    # human decision required
    # decision escalation
    ESCALATED = "ESCALATED"