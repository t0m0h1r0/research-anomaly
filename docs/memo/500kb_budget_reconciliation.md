# 500 KB Budget Reconciliation

status: DRAFT
created_at_utc: 2026-05-04T08:47:49Z
owner: ResearchArchitect

## PLAN

Reconcile the repository's 500 KB memory wording with the corrected deployment
assumption: a storage device may protect roughly 2000 volumes and have roughly
1 GB available for detector data. This gives an engineering target of about
500 KB per volume.

## EXECUTE

The corrected interpretation is:

- 500 KB is a per-volume detector-data budget, not a claim that all model
  runtime memory fits in 500 KB.
- The budget covers the model weight information needed for the detector and
  the input statistics/state needed to score one volume.
- Shared library/runtime memory, including the MNN runtime itself, is outside
  the 500 KB budget and should be amortized across the many-volume deployment.
- Transient inference scratch such as activation tensors, operator workspace,
  and reusable inference slots should still be measured for device fit, but it
  is a separate scheduling/peak-memory check rather than the root of the
  500 KB per-volume budget.

The arithmetic is intentionally approximate and uses 500 KB as a rounded
engineering target:

```text
1 GB / 2000 volumes ~= 500 KB per volume
```

If a target device specifies memory in binary units, then `1 GiB / 2000` is
about 524 KiB per volume. Keeping the project target at 500 KB is therefore a
conservative rounded budget. Because "1 GB" and "2000 volumes" are planning
assumptions rather than a target device measurement, manuscripts and design docs
should present 500 KB as an engineering budget to be validated, not as empirical
device evidence.

## VERIFY

Documents should avoid saying that 500 KB includes shared libraries, common MNN
heap, or all transient operator workspace. Device-fit gates should instead use
the following accounting terms:

```text
B_volume = 500 KB
V = protected volume count
Q = simultaneously allocated inference scratch slots
```

Persistent detector data:

```text
M_persistent(V) =
  M_shared_runtime
  + M_shared_weights
  + V * (M_volume_weights + M_volume_state)
```

Here `M_shared_weights` is nonzero only when one converted weight
representation can be shared across volumes. `M_volume_weights` is nonzero when
each volume needs a separate weight representation. The per-volume budget gate
is:

```text
shared-weight view:     (M_shared_weights / V) + M_volume_state <= B_volume
replicated-weight view: M_volume_weights + M_volume_state <= B_volume
```

Transient scratch is not part of the 500 KB root budget, but it is part of peak
device fit:

```text
M_peak(V, Q) = M_persistent(V) + Q * M_transient_scratch
```

The schedule must justify `Q`, because 2000 volumes scored every 10 seconds may
need more than one reusable inference slot.

## AUDIT

This memo is based on the user-provided deployment assumption in the
2026-05-04 ResearchArchitect task. It does not replace later target-device
measurements, MNN parity tests, or volume-scaling reports.
