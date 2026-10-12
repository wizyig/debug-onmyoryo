# Debug Onmyoryo

Observation First Debugging Framework

```text
Observe
  ↓
Interpret
  ↓
Preserve
  ↓
Audit
```

Debug Onmyoryo is a debugging and auditability framework focused on preserving observations before preserving conclusions.

## Core Principle

If a system cannot be observed, it cannot be audited.
If it cannot be audited, it cannot be trusted.

## Future Auditability

```text
FA = M ∨ G ∨ B

Maguro   = Trace Preservation
Goldfish = Interpretation Preservation
Mambo    = Existence Preservation
```

Observer is optional. Observation Space is mandatory.

## Components

| Component | Purpose |
|-----------|---------|
| Maguro    | Trace Preservation |
| Goldfish  | Interpretation Preservation |
| Mambo     | Existence Preservation |

## Fourth Exhibition Room

The Fourth Exhibition Room is an **Observation Enablement Space**, not an observer.
It guarantees that observation may occur. It does not specify who observes, nor does it guarantee correct interpretation or prediction.

## Positioning

This repository improves the efficiency of explaining observation and auditability requirements in bug-bounty and security research contexts.
Publishing the observation runtime and operators does not reproduce internal crystallization or proprietary processing paths.

## Quality Gates

- Global Coverage Gate (PR light / main full)
- Module Coverage Gate (full mode)
- Coverage Regression Protection
- Deterministic generation where applicable

## License

Apache License 2.0

See NOTICE and PATENTS.md.
