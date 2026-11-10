# Three-case challenger regression probe

This candidate combines typed local-model protocol checks with explicit challenger semantics. It does not approve assessments or establish model accuracy. Baseline: 1c41430cddfca21e661cdddceaa061ebbe99b6c2.

Run in PowerShell/PyCharm terminal with local Ollama already listening:

```powershell
python -m unittest discover -s cell_signaling -v
python -m cell_signaling.check_challenger --run
```

The second command makes at most three challenger calls, sequentially, with no retries or assessor call. It saves a unique diagnostic in local-output and prints the path. Any processing failure stops the probe and is not an evidence verdict. completed_needs_review means only that three responses passed protocol and structural validation. Read the saved reasons as well as labels.

The three synthetic cases assess a single hosted population. Fit and implementation remain constant. Execution varies between justified abstention, unsupported support, and abstention despite explicit timely evidence. The execution report explicitly dates review and decision recording separately; observation is December 2, avoiding the old November 30 metadata ambiguity. These cases test known failure modes, not held-out generalization. Expected judgments are draft reviewer expectations in examples/challenge_probe_review.json and never loaded by the runner or sent to the model. Do not modify a response or silently flip a label to match them.

The challenger now judges whether an assessment is justified, including correct abstention. A disagreement must identify the disputed assertion and evidentiary defect. The existing schema still cannot deterministically prove that a natural-language explanation agrees with its label. Human reasoning review remains required. The old assessment fixture's recording-date ambiguity remains documented, not silently relabeled; use this bounded probe before rerunning the full workflow.

Protocol correction: require assistant role and requested model in the response envelope; validate preflight inventory/model/version types. Malformed postflight metadata now follows the existing processing-failure path and clears the accepted summary. This does not cryptographically attest model identity, validate source truth, or prove safe behavior against all malicious input.

Offline validation: 71 tests pass, including three probe-boundary tests and five protocol regression tests. The first test attempt caught an import error in the new test module; it was corrected before the final freeze and passing run. No live inference was performed by the developer environment. Both passes of the normal pipeline still use the same model.
