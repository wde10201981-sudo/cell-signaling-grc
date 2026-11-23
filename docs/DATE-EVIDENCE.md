# Separate date handling experiment

This module is deliberately not connected to the frozen extraction or its live tests. Finish variant-05 first using:

```powershell
python -m cell_signaling.check_extraction_variants --case variant-05 --run
```

That command makes one local inference request with identical instructions, schema, packet and model options to case five of the original batch. It checks the frozen hashes and model identity, saves a separate report, and never reads reference answers. It does not complete or revise the prior failed report.

The separate `date_evidence` module preserves original text, reports exact/ambiguous/missing/invalid/unsupported dates, and separately assesses the deadline. For 01/02/2027 it retains January 2 and February 1; it does not choose a locale. Both are after December 31. If the deadline were January 15, the relation would remain not established.

Supported grammar is limited to ISO YYYY-MM-DD and numeric A/B/YYYY interpreted as DMY or MDY. Candidate conclusions are conditional on this grammar and calendar-date meaning. Other calendar systems, time zones, timestamps, relative dates, two-digit years and arbitrary prose are not supported. Explicit DMY/MDY selection requires a source reference; the helper checks presence, not authenticity. Missing or malformed dates never become evidence of failure.

A quoted-date entry point rejects transformed tokens and fabricated excerpts. Literal matching cannot establish whether the token is the completion date, belongs to the correct population or period, or comes from reliable/current evidence. The date helper alone makes no coverage or compliance judgment. Expert review and upstream scope checks remain necessary.

Future integration needs a separately versioned extraction contract with a raw date field; it must not silently reinterpret old results. Keep the current frozen prompt unchanged until the remaining live case has been reviewed. Offline tests validate date arithmetic and provenance checks, not model accuracy.
