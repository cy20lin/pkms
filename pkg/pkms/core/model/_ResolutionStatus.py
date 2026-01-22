from enum import Enum

class ResolutionStatus(str, Enum):
    # The file is found, and is in good state.
    OK      = "OK"

    # The file is trashed (soft-deleted), and record is found in DB
    TRASHED = "TRASHED"

    # The file is deleted and gone, only record found in DB
    DELETED = "DELETED"

    # The file is comfirmed not found in the record and not in the filesystem vault as well
    # > ABSENT is used to indicate confirmed non-existence of a resource.
    # > The term avoids the alarmist and investigative connotations of MISSING,
    # > which are inappropriate for normal resolution outcomes.
    ABSENT  = "ABSENT"


