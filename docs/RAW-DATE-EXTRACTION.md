# Raw-date extraction 0.3

Run locally with Ollama running:

```powershell
git pull --ff-only
python -m cell_signaling.check_raw_dates --run
```

This new entry point reuses the five variant input packets, with the same Qwen model and settings, but a separately versioned prompt and schema. It does not alter extraction 0.2, the original probes or their saved reports. Frozen-file verification still checks the old baseline. The new response field is raw_completion_date instead of completed_on. The model must copy the original source text rather than convert date formats. Code checks exact quotations and date tokens, then derives candidate interpretations and deadline relationships.

For 01/02/2027, retain both 2027-01-02 and 2027-02-01, no exact date, and after_deadline against 2026-12-31. Against 2027-01-15, timeliness is not established. Candidate dates before the assigned period require review. Conflicting completion/noncompletion accounts still require review. Disparate candidate sets across completed accounts are conservatively sent for review, not reconciled automatically. Missing, invalid or unsupported dates do not establish timely execution or nonperformance.

Date interpretation is conditional on Gregorian ISO/DMY/MDY formats only. The AI cannot select the convention through the response. Source quotation matching cannot prove the date belongs to the right activity, population or period; those semantic judgments remain part of evaluation and expert review. A null raw date can also reflect a model omission. There is no claim of complete coverage, source truth or customer readiness.

This is a regression run informed by the earlier failure, not an unseen evaluation. Separate draft reviewer expectations are in examples/raw_date_review.json and must not enter requests. Expected final results match the previous variants except variant-04: it now retains ambiguity while establishing lateness under both supported numeric conventions. Inspect raw text, candidate dates and correct population attribution, not just labels. All original source snapshots and raw outputs remain in the saved report. Processing failures and failed final model checks remain diagnostic-only. No automatic retries or changes to approvals occur.
