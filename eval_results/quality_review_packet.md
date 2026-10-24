# Actual golden-output review packet

All AFTER assertions, expected schema and completion checks pass. Outputs changed; no human review or approval has been recorded. These fixed synthetic cases are limited evidence, not universal behavioral equivalence.

Task: `ce8235f44907792f94c9c15b`; implementation commit: `b7aecbcb5f388f37a54b1a9b51ca0bfe22cf5d2f`.
Source SHA-256: `4a60ea8b1d9be129400f306f703808100a10a6dc961a4e2f6f92e29a50171b0c`.
Diff SHA-256: `bb144678b3d0c9c09dd4e719bef2a7123441d691f94c5a839652cdd2dd6c5625`.
[Raw actual collection](quality_guard/ce8235f44907792f94c9c15b-calendar.json), SHA-256 `6bc6840de21446c9fbee25fa472c00b1bd1ba89a23ae75b70d6626a55a9a831d`.

The case clock is recorded as 2026-10-24; it is intentionally independent of the current wall-clock date. Original fixed inputs, expected answers, model, temperature, seed and budget were unchanged.

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

1. **Which item** from the order you would like to return.
2. **Your reason** for the return (e.g., change of mind, damaged goods, incorrect item, etc.).
3. **The remedy you prefer** (e.g., refund, exchange, repair).

Once you provide this, I will check the eligibility and next steps based on the order details and policy.

Please share these details so I can guide you further.
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
