# CarePulse Progress Log

Use this log to record small daily improvements and what was learned from each one.

| Day | Date | Area | What changed | What I learned | Commit |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-27 | Project motivation | Added daily practice structure and project learning notes | CarePulse connects support experience with customer risk, recovery, and follow-up workflows | Day 1: add daily practice plan |
| 11 | 2026-10-07 | Follow-up ownership | Added a clear agent-page view for case owner, latest action owner, status, follow-up note, and missing review point | Existing intervention records can explain ownership, while the current model does not yet store a review date | Improve follow-up ownership clarity |
| 12 | 2026-10-08 | Risk explanation | Clarified why a case received its risk band by showing the evidence signals and point contributions together | Risk decisions are easier to review when the scoring signals are visible beside the band | Explain risk band drivers |
| 13 | 2026-10-09 | Dashboard usefulness | Added a threshold-aware explanation and a direct link from the high-risk count to the risk monitor | Dashboard metrics are more useful when their meaning and next action are visible together | Make the risk count actionable |
| 14 | 2026-10-10 | Dashboard action validation | Added a test confirming the dashboard's high-risk action links users to the risk monitor | Small UI actions are safer when important navigation is covered by an automated test | Day 14: test dashboard risk monitor action |
| 15 | 2026-10-11 | Risk-monitor clarity | Explained that the queue starts with the highest-risk journeys and added a focused test for the manager's next action | A risk list is more useful when its priority and next step are clear before someone opens a case | Day 15: clarify the risk-monitor queue |
| 16 | 2026-10-12 | Backend validation | Added a focused test confirming that equal medium and high risk thresholds are rejected | Risk bands need an unambiguous ordering so managers can trust the configuration | Day 16: test equal risk thresholds |

| 17 | 2026-10-13 | Deployment readiness | Clarified the production session-signing-key requirement in the run guide | A demo secret is acceptable only for local synthetic demo use; production needs a unique value outside source control | Day 17: clarify production secret setup |

| 18 | 2026-10-14 | Deployment readiness | Made the environment example clearly separate demo settings from production-only values | Environment templates should guide safe setup without containing a real secret | Day 18: make environment setup safer |

| 19 | 2026-10-15 | Login safety | Added a regression test confirming that login ignores an external redirect target | Login return paths need to stay inside the application to protect users from misleading redirects | Day 19: test safe login redirects |

| 20 | 2026-10-16 | Login safety | Added a regression test confirming a valid internal login return path with query parameters is preserved | Safe redirect checks should block external destinations without breaking legitimate navigation inside the app | Day 20: test safe internal login redirect |

| 21 | 2026-10-17 | Login safety | Hardened login return-path validation to reject ambiguous backslash-based paths and added a regression test | Redirect validation should allow normal internal navigation while rejecting path forms that browsers or proxies may interpret unexpectedly | Day 21: harden login return paths |

## Notes format

Keep each note short and honest:

- What business problem did this touch?
- Which part of the project did it involve?
- Which tool, language, or framework did it help you understand?
- How would you explain it in an interview?
