# Actual golden-output review packet

All AFTER assertions, expected schema and completion checks pass. Outputs changed; no human review or approval has been recorded. These fixed synthetic cases are limited evidence, not universal behavioral equivalence.

Task: `1733e486db3c2fd68eff119b`; implementation commit: `0dff063b152eee2f62710b30abd03d17ae1c5d8c`.
Source SHA-256: `c988685ccc5ec3ed637a4b384df94a8d51886492df7e3b766a7c030ab16bc27b`.
Diff SHA-256: `4b688cd47b6f8f56733c90c10ceb4b2b69b5db48eda7aa30c55e3f00de76961d`.
[Raw actual collection](quality_guard/1733e486db3c2fd68eff119b-calendar.json), SHA-256 `29ac15ba14bb0c1f57c97b177b503b15f8c06daef673bb81fedfd6e859b605b6`.

The case clock is recorded as 2026-10-24; it is intentionally independent of the current wall-clock date. Original fixed inputs, expected answers, model, temperature, seed and budget were unchanged.

Review the authorization response, retained conversation fact, French response, retrieved identifier and corrected date output below. Approval requires accepting all five changed outputs and reviewing the PR diff.

## golden-authorization

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

## golden-continuity

BEFORE:

```text
unknown
```

AFTER:

```text
cobalt
```

## golden-locale

BEFORE:

```text
Pour vérifier la livraison de votre colis, veuillez me fournir le numéro de référence de votre commande. Cela me permettra de consulter l'état de votre colis et de vous informer sur sa livraison ou sur les étapes suivantes.
```

AFTER:

```text
Pour vérifier la livraison de votre colis, veuillez fournir le numéro de référence de votre commande. Cela nous permettra de consulter l'état actuel de l'expédition et de vérifier si le colis a été livré ou s'il y a un retard.
```

## golden-retrieval

BEFORE:

```text
RETIRED-SYN-582
```

AFTER:

```text
RETRIEVAL-SYN-582
```

## golden-time

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
