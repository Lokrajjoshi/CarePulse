# Sentiment guide

CarePulse treats sentiment as an early interaction signal, not a replacement for the final survey. It can receive a chat reply, email body, or voice transcript excerpt, classify the message as positive, neutral, or negative, and attach a confidence/explanation. The later CSAT, DSAT, or recommendation survey becomes the outcome used for calibration and analysis.

The generator stores synthetic ground truth. The API also runs local VADER sentiment with business rules for terse acknowledgements such as `hmm`, `okay`, `right`, and `noted`, which should remain neutral until more context arrives. Explicit frustration cues such as `still waiting`, `no update`, `third time`, and `unacceptable` receive a negative signal. VADER is a lightweight lexical demonstration; it cannot know a person's emotion with certainty, and synthetic labels are not evidence about real customers.

A production organization would train/calibrate this layer from consented, policy-approved historical conversations labelled by human review and aligned with post-interaction surveys. The system should measure precision, recall, false positives, false negatives, drift, language/channel differences, and agent feedback before using it operationally.
