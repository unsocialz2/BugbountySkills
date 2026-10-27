# Experiment coverage — <target>

| Test / hypothesis ID | Feature / route / version | Actor / tenant / role | Resource ownership | Action / representation | Lifecycle / auth state | Control / prediction | Observed result | Verdict | Evidence / date | Gap / next step / superseded by |
|----------------------|---------------------------|-----------------------|--------------------|-------------------------|------------------------|----------------------|-----------------|---------|-----------------|-----------------|

Verdicts: `not-tested`, `blocked`, `inconclusive`, `enforced-in-tested-case`, `boundary-failure`.
Use only those verdicts; put descriptions such as “no reflection” or “UI upgrade prompt” in Observed result. Evidence references must identify a saved artifact and section, not “session logs” without a location. Missing capture is an evidence gap.

Preserve historical rows and link superseding test IDs. Current blocked/not-tested lists must reflect later successful access. One row may summarize a homogeneous batch only if its membership, exceptions, and evidence are traceable.

A verdict covers only the recorded tuple. Link request/response or runtime evidence; use sanitized identity labels. Verify the session and legitimate control before interpreting a negative test. Capture independent state reads and transient effects when relevant. Record product/version or auth changes that invalidate earlier evidence.
