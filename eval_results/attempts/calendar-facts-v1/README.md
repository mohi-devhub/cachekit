# Calendar facts v1 — blocked

Actual unchanged five-case collection after adding elapsed days and an exceeds-
window comparison. The calculator supplied the correct 34 elapsed days, but the
model still answered within_window=true. The original expected answer remains
false and approval is blocked. The complete original outputs and evaluated case
checks are preserved; this attempt did not proceed to performance replay.

A later calculator version adds the direct mathematical closed-window comparison
so the model can read the value without negating the exceeds-window flag.
