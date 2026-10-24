# Actual golden-output review packet

Recorded 2026-10-25T02:52:56+05:30. Suite: **helpdesk-e5-lite-v2**.

Overall quality status: **passed**. Mohith acceptance is recorded for the exact outputs; exact-diff approval and merge are separate.

All five recorded inputs, date schema, model, temperature, seed and output budget are unchanged. V2 adds the requested explicit return/escalation confirmation assertions. Earlier v1 runs remain historical and are not relabeled.

Task: `9fc9012aabdf18de95f76598`; implementation commit: `b600ed210749ea1969a2136db6307af457bf4cc5`.
Source SHA-256: `a2e81b98660ef4c7d59cb099cb961fc74e6b27fdce4497dc895eaf4798ab8aab`.
Diff SHA-256: `9892ffb9ee39be22a43bb090ea9d5069630a5cc1590903b4da5fe9771bb081c0`.
[Raw actual collection](quality_guard/9fc9012aabdf18de95f76598-calendar.json), SHA-256 `761395061e0ff7480c002a09a278ae17186e7f5ed9ae92038c3f836626713e36`.
[Deterministic investigation and original expected answer](golden_case_investigation.json).

**semantic change: restores behavior lost by reordering, found by the quality guard**. The one response instruction is an explicitly authorized exception, not part of the reorder.
[Original failing v2 run and review](attempts/confirmation-omission-v2/README.md) remain preserved; no failure is overwritten.
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

Failed assertions cannot be accepted away. Changed passing outputs still need human review. This five-case suite is bounded evidence, not universal semantic equivalence. Any different answer still needs explicit human review. Final source verification and exact-diff approval are separate.
