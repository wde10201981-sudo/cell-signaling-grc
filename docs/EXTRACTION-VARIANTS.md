# Frozen extraction comparison

Run with local Ollama already running:

```powershell
git pull --ff-only
python -m cell_signaling.check_extraction_variants --run
```

This additive experiment leaves the extraction implementation, instructions, schema, adapter settings and original runner unchanged at baseline 51e48301f1a0c2f277a9fe9c21a8a9253d7fd485. A hash manifest verifies those files and the new input set before any model requests. Windows CRLF checkouts are supported. Do not edit frozen files to make results pass.

Five synthetic variants test paraphrased completion, a plan without completion evidence, on-premises missing information beside AWS completion, an ambiguous non-ISO completion date, and distinct completion dates for AWS versus on-premises. Source population metadata is the assigned retrieval scope; document text can discuss other populations. These cases test whether extraction respects the assignment inside mixed text. They do not validate enterprise entity resolution or cross-tenant access controls.

The unchanged contract only accepts literal ISO completion dates. An explicitly completed review with a non-ISO date should retain completion but return a null date, leaving timeliness not established by this narrow rule. This limitation must not be confused with proof of nonperformance.

Draft reviewer expectations live separately in examples/extraction_variants_review.json and are never loaded by the runner. These examples were authored after freezing the prompt and before any live run; they are not independently authored or statistically representative. Once used to change prompts, they become regression cases, not unseen evaluation cases.

Review all extracted assertions, date attribution and quotations in the saved JSON, not just final labels. In particular, a quotation can match a source while describing the wrong population. Expected results do not verify source truth. Processing failures stop the unchanged runner; unattempted cases remain untested. No retry, automatic prompt adjustment or approval occurs. Offline tests exercise the harness only; the user must perform the real local-model run.
