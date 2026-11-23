"""Separate deterministic date experiment; not connected to frozen AI extraction."""
import re
from datetime import date

VERSION = 'date-evidence-0.1'


def interpret_date(raw_date, deadline, *, convention='unknown', convention_reference=None):
    """Interpret one already-attributed date token, preserving its original text.

    Supported grammar: YYYY-MM-DD or A/B/YYYY (DMY and MDY only).
    Attribution to the right activity/population is an upstream review obligation.
    Explicit DMY/MDY conventions require a source reference, not a model guess.
    """
    if not isinstance(deadline, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', deadline):
        raise ValueError('Deadline must be an exact ISO date')
    end = date.fromisoformat(deadline)
    if convention not in ('unknown', 'DMY', 'MDY'):
        raise ValueError('Unsupported date convention')
    if convention != 'unknown' and not (isinstance(convention_reference, str) and convention_reference.strip()):
        raise ValueError('Explicit convention requires a source reference')
    if raw_date is not None and not isinstance(raw_date, str):
        raise ValueError('Raw date must be text or null')
    result = {'version': VERSION, 'raw_date': raw_date, 'date_status': 'missing',
              'exact_date': None, 'candidate_dates': [], 'deadline': deadline,
              'deadline_relation': 'not_established', 'convention': convention,
              'convention_reference': convention_reference,
              'interpretation_basis': 'Only ISO, DMY and MDY calendar dates are supported; no locale inference.',
              'requires_source_review': True}
    if raw_date is None or not raw_date.strip():
        return result
    token = raw_date.strip()
    candidates = set()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', token):
        try:
            candidates.add(date.fromisoformat(token))
        except ValueError:
            pass
    elif re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', token):
        a, b, year = map(int, token.split('/'))
        conventions = ('DMY', 'MDY') if convention == 'unknown' else (convention,)
        for order in conventions:
            month, day = (b, a) if order == 'DMY' else (a, b)
            try:
                candidates.add(date(year, month, day))
            except ValueError:
                pass
    else:
        result['date_status'] = 'unsupported_format'
        return result
    if not candidates:
        result['date_status'] = 'invalid'
        return result
    result['candidate_dates'] = sorted(d.isoformat() for d in candidates)
    result['date_status'] = 'exact' if len(candidates) == 1 else 'ambiguous'
    if len(candidates) == 1:
        result['exact_date'] = result['candidate_dates'][0]
    if all(d <= end for d in candidates):
        result['deadline_relation'] = 'on_or_before_deadline'
    elif all(d > end for d in candidates):
        result['deadline_relation'] = 'after_deadline'
    return result


def interpret_quoted_date(source_text, quote, raw_date, deadline, **kwargs):
    """Check literal provenance before interpreting; does not prove semantic attribution."""
    if not isinstance(source_text, str) or not isinstance(quote, str) or not quote.strip() or quote not in source_text:
        raise ValueError('Quote must be an exact nonempty source excerpt')
    if not isinstance(raw_date, str) or not raw_date.strip():
        raise ValueError('A quoted date requires nonempty original text')
    # Prevent accepting a normalized date or a substring of a longer date token.
    if not re.search(r'(?<![\w/-])' + re.escape(raw_date) + r'(?![\w/-])', quote):
        raise ValueError('Original date text must appear as a complete token in the quote')
    result = interpret_date(raw_date, deadline, **kwargs)
    result['source_quote'] = quote
    return result
