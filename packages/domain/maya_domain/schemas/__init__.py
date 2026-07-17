"""Pydantic DTOs (schemas) for the MayaDesk domain package.

These are pure data-transfer objects: no SQLAlchemy imports, no ORM
dependencies. They validate input at the API boundary and shape output for
serialization.
"""

from __future__ import annotations

from maya_domain.schemas.appointment import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentUpdate,
)
from maya_domain.schemas.audit import AuditLogCreate, AuditLogRead, AuditLogUpdate
from maya_domain.schemas.availability import (
    AvailabilityCreate,
    AvailabilityRead,
    AvailabilityUpdate,
)
from maya_domain.schemas.call_log import CallLogCreate, CallLogRead, CallLogUpdate
from maya_domain.schemas.callback import CallbackCreate, CallbackRead, CallbackUpdate
from maya_domain.schemas.conversation import (
    ConversationMessageCreate,
    ConversationMessageRead,
    ConversationMessageUpdate,
)
from maya_domain.schemas.pagination import Page, PageParams
from maya_domain.schemas.patient import PatientCreate, PatientRead, PatientUpdate

__all__ = [
    # Patient
    "PatientCreate",
    "PatientUpdate",
    "PatientRead",
    # Availability
    "AvailabilityCreate",
    "AvailabilityUpdate",
    "AvailabilityRead",
    # Appointment
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentRead",
    # Callback
    "CallbackCreate",
    "CallbackUpdate",
    "CallbackRead",
    # CallLog
    "CallLogCreate",
    "CallLogUpdate",
    "CallLogRead",
    # ConversationMessage
    "ConversationMessageCreate",
    "ConversationMessageUpdate",
    "ConversationMessageRead",
    # AuditLog
    "AuditLogCreate",
    "AuditLogUpdate",
    "AuditLogRead",
    # Pagination
    "Page",
    "PageParams",
]
