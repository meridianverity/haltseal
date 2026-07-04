# Security and limitations

This repository is not a production security boundary.

The verifier is intentionally small so reviewers can inspect the public concepts: canonical action binding, permit status, signed-head freshness, continuity posture, replay denial, and evidence record shape.

Limitations:

- Synthetic signatures use deterministic fixture HMACs.
- The signed-head and continuity mechanisms are simulated.
- The replay cache is in-memory.
- No driver, firmware, hypervisor, accelerator, cloud, robotics, or endpoint hook is included.
- No commercial deployment rights are granted.
- No patent license is granted.
