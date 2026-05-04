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

The arithmetic is intentionally approximate:

```text
1 GB / 2000 volumes ~= 500 KB per volume
```

Because "1 GB" and "2000 volumes" are planning assumptions rather than a target
device measurement, manuscripts and design docs should present 500 KB as an
engineering budget to be validated, not as empirical device evidence.

## VERIFY

Documents should avoid saying that 500 KB includes shared libraries, common MNN
heap, or all transient operator workspace. Device-fit gates should instead
separate:

```text
M_total(V) =
  M_shared_runtime
  + M_shared_weights
  + V * M_volume_state
```

or, when weights cannot be shared across volumes:

```text
M_total(V) =
  M_shared_runtime
  + V * (M_volume_weights + M_volume_state)
```

The conservative per-volume check remains:

```text
M_volume_weights + M_volume_input_statistics <= 500 KB
```

## AUDIT

This memo is based on the user-provided deployment assumption in the
2026-05-04 ResearchArchitect task. It does not replace later target-device
measurements, MNN parity tests, or volume-scaling reports.
