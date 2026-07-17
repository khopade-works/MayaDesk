"""ORM models package.

Importing this package registers every concrete model with ``Base.metadata``
so Alembic autogenerate and ``create_all`` can discover the full schema. All
model classes and shared enums are re-exported for convenient importing.
"""

from maya_domain.database.base import Base
from maya_domain.models.appointment import Appointment
from maya_domain.models.audit import AuditLog
from maya_domain.models.availability import Availability
from maya_domain.models.call_log import CallLog
from maya_domain.models.callback import Callback
from maya_domain.models.conversation import ConversationHistory
from maya_domain.models.enums import (
    AppointmentStatus,
    CallOutcome,
    CallbackPriority,
    CallbackStatus,
    ConversationRole,
)
from maya_domain.models.mixins import TimestampMixin
from maya_domain.models.patient import Patient

__all__ = [
    "Base",
    "TimestampMixin",
    # Models
    "Patient",
    "Availability",
    "Appointment",
    "Callback",
    "CallLog",
    "ConversationHistory",
    "AuditLog",
    # Enums
    "AppointmentStatus",
    "CallbackPriority",
    "CallbackStatus",
    "CallOutcome",
    "ConversationRole",
]
