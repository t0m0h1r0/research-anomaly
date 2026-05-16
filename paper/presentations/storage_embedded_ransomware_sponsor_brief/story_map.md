# Story Map

take_home_message: >
  This is not a deployment claim; it is a technical decision path for testing
  whether block-storage-side, 10-second metadata can justify a tiny AE under
  strict memory and scheduling gates.

story_pattern: technical_value_adoption

audience_transformation:
  before: Embedded ransomware ML is an unclear idea that may depend on host context or oversized models.
  after: The project has explicit boundaries, cheap inputs, candidate complexity tests, and rejection gates.

arc:
  situation: Ransomware writes still cross the block-storage boundary even when host context is unavailable.
  tension: The storage device can only afford cheap statistics, small per-volume state, and scheduled CPU windows.
  recommendation: Treat AE as a candidate to earn its place after simple rules and before any device-readiness claim.
  evidence: Use the fixed 10-second feature contract, AE-01..05 ladder, 500 KB detector-data accounting, and MNN parity plan.
  decision_ask: Decide the next evidence package: offline comparison, MNN parity, detector-data measurement, or scheduling harness.

slide_functions:
  - slide: 1
    role: technical scope and observation boundary
  - slide: 2
    role: decision frame by the second slide
  - slide: 3
    role: input contract proof object
  - slide: 4
    role: model candidate ladder
  - slide: 5
    role: memory and scheduling proof object
  - slide: 6
    role: evaluation gates and close

