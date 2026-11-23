# Focused execution evidence experiment

Use this probe next instead of rerunning the two-agent challenger. The existing workflow is retained for comparison; this experiment does not replace it or approve coverage.

```powershell
git pull --ff-only
python -m unittest discover -s cell_signaling -v
python -m cell_signaling.check_extraction --run
```

Keep local Ollama running. Qwen3 8B receives five synthetic cases, one at a time, with no second agent and no retries. The command saves the exact inputs, requests, extracted facts, model settings and rule outputs to local-output. Send the saved JSON for review. Without --run, no model is contacted.

The task is only review completion for one requirement, population and period. AI extracts an explicit completion statement and optional exact ISO date from each source. Code validates source IDs, quote matching, dates, source scope and complete source accounting; then applies deterministic rules. Timely completion is supported_execution, missing information is not_established, explicit nonperformance or late completion is adverse_evidence, and incompatible completion accounts require review. Completed without an explicit date does not establish timeliness.

The five examples cover timely, missing, explicitly not performed, late and contradictory accounts. Reviewer expectations remain in extraction_review.json and are never loaded into requests. These are authored regression examples, not an independent held-out benchmark. No live inference was performed in the development environment.

Boundaries: supplied source population and period are trusted synthetic intake metadata, not discovered entity mappings. This experiment does not evaluate control fit, implementation, decision-recording obligations, general requirement coverage, or source truth. It does not handle arbitrary date formats, source withdrawals, historical revisions or freshness policy; those remain separate framework concerns. A matching quote can still be misinterpreted. In particular, a model can quote a negative statement but classify it as completed, or overlook a completion statement. Offline validation cannot prove that those semantic failures are absent. Review every extracted assertion before trusting the deterministic result. Same facts in code yield repeatable rules, not guaranteed true inputs.

Source instructions are data and never authorize tools. No approvals, customer-system changes, or operational actions occur. Processing failures remain diagnostic-only rather than becoming an evidence verdict. The old challenger experiment remains available, but focus on this narrower test before changing model or adding agents.

Version execution-extraction-0.2 permits an optional exact source excerpt for not_stated, while requiring a null completion date. Empty excerpts remain valid. This preserves explanations of missing information without converting them into completion evidence; invented or wrong-source excerpts remain rejected.
