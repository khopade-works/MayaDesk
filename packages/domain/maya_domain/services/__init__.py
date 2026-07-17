"""Application services: use cases orchestrating repositories within a unit of work.

Services take a session, coordinate one or more repositories, and return small
result DTOs. They do not open transactions themselves — the caller wraps them in
``maya_domain.database.unit_of_work`` so the commit boundary lives in one place.
"""

from maya_domain.services import dashboard_service
from maya_domain.services.availability_service import list_open_slots
from maya_domain.services.booking_service import book_appointment
from maya_domain.services.callback_service import request_callback
from maya_domain.services.patients import get_or_create_patient
from maya_domain.services.results import BookingResult, CallbackResult, OpenSlot

__all__ = [
    "list_open_slots",
    "book_appointment",
    "request_callback",
    "get_or_create_patient",
    "dashboard_service",
    "OpenSlot",
    "BookingResult",
    "CallbackResult",
]
