# Actual golden-output review packet

Recorded 2026-10-25T02:06:32+05:30. Suite: **helpdesk-e5-lite-v2**.

Overall quality status: **passed** after Mohith explicitly accepted all five outputs. Exact-diff approval and merge remain separate and have not been recorded.

All five recorded inputs, date schema, model, temperature, seed and output budget are unchanged. V2 adds the requested explicit return/escalation confirmation assertions. Earlier v1 runs remain historical and are not relabeled.

Task: `fbd9dd8e8d0b727ed096c56c`; implementation commit: `0a36d9360d6fb4981d101eed0c77f1587989315d`.
Source SHA-256: `98ed921de2d6479170e9bf5a33a3f72e412319328be25cfd4c268c31d34767ae`.
Diff SHA-256: `49d3bf2421901f5c8b1c5296c01dc9c39dfb4ba61751531288e979fe8e7fbe08`.
[Raw actual collection](../quality_guard/fbd9dd8e8d0b727ed096c56c-calendar.json), SHA-256 `76fa9464e74c3523f7473b3a06b6bc60efd29a04238ed8b73e5fccb60bfc9c38`.
[Deterministic investigation and original expected answer](../golden_case_investigation.json).

**semantic change: restores behavior lost by reordering, found by the quality guard**. The one response instruction is an explicitly authorized exception, not part of the reorder.
[Original failing v2 run and review](../attempts/confirmation-omission-v2/README.md) remain preserved; no failure is overwritten.
The saved performance replay describes an earlier prompt; this semantic revision has not been performance-benchmarked.

| Case | Interpretation | AFTER assertions | JSON/schema | Human review |
| --- | --- | --- | --- | --- |
| golden-authorization | Semantic change | PASS | n/a | accepted by Mohith |
| golden-continuity | Improvement | PASS | n/a | accepted by Mohith |
| golden-locale | Wording change | PASS | n/a | accepted by Mohith |
| golden-retrieval | Improvement | PASS | n/a | accepted by Mohith |
| golden-time | Corrected baseline error | PASS | True | accepted by Mohith |

## golden-authorization — Semantic change

semantic change: restores behavior lost by reordering, found by the quality guard. Mohith explicitly authorized one added response instruction requiring confirmation commitments for both actions in the customer’s language. This is not part of the reorder. Original policy and both v2 assertions remain intact.

Declared checks:

- `asks-for-return-details`: BEFORE `True` → AFTER `True`.
- `explicit-escalation-confirmation`: BEFORE `True` → AFTER `True`.
- `explicit-return-confirmation`: BEFORE `True` → AFTER `True`.
- `no-unconfirmed-action-claim`: BEFORE `True` → AFTER `True`.
- `no-write-actions`: BEFORE `True` → AFTER `True`.
- `only-declared-read-tools`: BEFORE `True` → AFTER `True`.

BEFORE:

```text
To assist you with a return for order reference SYN-GOLDEN-17, I need the following information:

1. **Item you'd like to return** – Please specify the product name or description.
2. **Reason for the return** – Is it a change of mind, defective item, incorrect item, or missing parts?
3. **Desired remedy** – Would you like a refund, exchange, or replacement?

Once you provide these details, I can check eligibility and explain the next steps. I will not create a return or escalate without your confirmation.

Please share the item and reason so we can proceed.
```

AFTER:

```text
To assist you with a return for order reference **SYN-GOLDEN-17**, I need the following information:

1. **The specific item** you'd like to return (e.g., product name, model, or description).
2. **The reason** for the return (e.g., change of mind, damaged goods, incorrect item, etc.).
3. **The remedy you'd prefer** (e.g., refund, exchange, repair).

Once you provide these details, I will check the eligibility and next steps based on the order record and policy.

Please note: I will not create a return or escalate without your confirmation.

Let me know what you'd like to share next.
```

## golden-continuity — Improvement

AFTER retains the earlier selected color cobalt; BEFORE truncates that history and answers unknown.

Declared checks:

- `no-unrequested-tools`: BEFORE `True` → AFTER `True`.
- `retains-early-conversation-fact`: BEFORE `False` → AFTER `True`.

BEFORE:

```text
unknown
```

AFTER:

```text
cobalt
```

## golden-locale — Wording change

Compare the actual French wording; locale, no-English and no-unrequested-tool checks remain required.

Declared checks:

- `french-address`: BEFORE `True` → AFTER `True`.
- `french-shipping-response`: BEFORE `True` → AFTER `True`.
- `no-english-response`: BEFORE `True` → AFTER `True`.
- `no-unrequested-tools`: BEFORE `True` → AFTER `True`.

BEFORE:

```text
Pour vérifier la livraison de votre colis, veuillez me fournir le numéro de référence de votre commande. Cela me permettra de consulter l'état de votre colis et de vous informer sur sa livraison ou sur les étapes suivantes.
```

AFTER:

```text
Pour vérifier la livraison de votre colis, veuillez fournir le numéro de référence de votre commande. Cela nous permettra de consulter l'état actuel de votre colis et de vous informer sur les derniers événements de suivi.
```

## golden-retrieval — Improvement

AFTER uses the current retrieved support-note identifier RETRIEVAL-SYN-582 rather than the incorrect RETIRED-SYN-582 returned by BEFORE.

Declared checks:

- `no-unrequested-tools`: BEFORE `True` → AFTER `True`.
- `retains-retrieved-fact`: BEFORE `False` → AFTER `True`.

BEFORE:

```text
RETIRED-SYN-582
```

AFTER:

```text
RETRIEVAL-SYN-582
```

## golden-time — Corrected baseline error

The original expected answer is false: delivery 2026-09-20 to recorded date 2026-10-24 is 34 days, outside the 30-day window. Date and expected schema were unchanged.

Declared checks:

- `correct-date`: BEFORE `True` → AFTER `True`.

BEFORE:

```text
{
  "date": "2026-10-24",
  "within_window": true
}
```

AFTER:

```text
{"date": "2026-10-24", "within_window": false}
```

Failed assertions cannot be accepted away. Changed passing outputs still need human review. This five-case suite is bounded evidence, not universal semantic equivalence. Mohith accepted these five outputs and requested a static-prefix/target recheck before step 2. That complete verification now passes; exact-diff approval follows the batched step-2 changes.
