"""Authoritative normalized interface entry point (journal/2 only)."""
import adapter
from strict_ledger import parse
from selector_v2.registered_ledger import JOURNAL_VERSION, RegisteredLedger


def open_gateway(raw, *, authenticate=None):
    """Return the actual core ledger, not a wrapper or parallel state.

    authenticate(request_bytes, exact_input_bytes, registration_bytes) is an
    optional owner hook; no verified operational acceptance is exposed.
    """
    if JOURNAL_VERSION != 'selector-v2-journal/2':
        raise ValueError('unsupported core journal version')
    return RegisteredLedger(raw, adapter=adapter, parse=parse, authenticate=authenticate)
