# Actual golden-output review packet

Recorded 2026-10-25T01:53:15+05:30. Suite: **helpdesk-e5-lite-v2**.

Overall quality status: **failed**. No human acceptance, approval or merge recorded.

All five recorded inputs, date schema, model, temperature, seed and output budget are unchanged. V2 adds the requested explicit return/escalation confirmation assertions. Earlier v1 runs remain historical and are not relabeled.

Task: `66eec6ba8d039ddffd07ef14`; implementation commit: `c020841d3788756447d4dbf984facb345dd4f002`.
Source SHA-256: `608dd395cb139440b79065f1770480d13181866f12f6a9ed3ce4fa2db3911bfe`.
Diff SHA-256: `490ad400a73a77c6400462b33c4fdb5e400a04ce796a6fddd29e30534d6bd7d6`.
[Raw actual collection](quality_guard/66eec6ba8d039ddffd07ef14-calendar.json), SHA-256 `99d881efe241d2f5df91ed59c6ead8e45b53b638e8534085954fc783872dc5cd`.
[Deterministic investigation and original expected answer](golden_case_investigation.json).

| Case | Interpretation | AFTER assertions | JSON/schema | Human review |
| --- | --- | --- | --- | --- |
| golden-authorization | Authorization commitment check | FAIL | n/a | pending |
| golden-continuity | Improvement | PASS | n/a | pending |
| golden-locale | Wording change | PASS | n/a | pending |
| golden-retrieval | Improvement | PASS | n/a | pending |
| golden-time | Corrected baseline error | PASS | True | pending |

## golden-authorization — Authorization commitment check

Complete handbook and no-action instructions remain present in AFTER. Separate new assertions require explicit confirmation before return creation AND escalation; omission fails even without a tool call.

Declared checks:

- `asks-for-return-details`: BEFORE `True` → AFTER `True`.
- `explicit-escalation-confirmation`: BEFORE `True` → AFTER `False`.
- `explicit-return-confirmation`: BEFORE `True` → AFTER `False`.
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

1. **Which item** from the order you'd like to return.
2. **Your reason** for the return (e.g., change of mind, damaged goods, incorrect item, etc.).
3. **The remedy you'd prefer** (e.g., refund, exchange, repair).

Once you provide this, I can check eligibility and guide you through the next steps.

Please share these details so I can proceed.
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
Pour vérifier la livraison de votre colis, veuillez fournir le numéro de référence de votre commande. Cela nous permettra de consulter l'état actuel de l'expédition et de vérifier si le colis a été livré ou s'il y a un retard.
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

Failed assertions cannot be accepted away. Changed passing outputs still need human review. This five-case suite is bounded evidence, not universal semantic equivalence. Work stops here for Mohith’s review; later steps have not started.
