# CarePulse Progress Log

Use this log to record small daily improvements and what was learned from each one.

| Day | Date | Area | What changed | What I learned | Commit |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-27 | Project motivation | Added daily practice structure and project learning notes | CarePulse connects support experience with customer risk, recovery, and follow-up workflows | Day 1: add daily practice plan |
| 2 | 2026-09-29 | Risk scoring | Added a test for missed-promise risk scoring | Risk logic is safer when important scoring behaviour is covered by a focused test | Day 2: test missed-promise risk scoring |
| 3 | 2026-09-29 | Risk queue | Showed case owners in the risk queue | Risk lists are more actionable when ownership is visible | Day 3: show case owners in risk queue |
| 4 | 2026-09-30 | Recovery actions | Added a test for recovery-action status validation | Workflow actions need validation so unsupported states are rejected | Day 4: test recovery action status validation |
| 5 | 2026-10-01 | Promise reliability | Clarified the promise-reliability metric | A metric is more useful when users can understand what contributes to it | Day 5: explain promise reliability metric |
| 6 | 2026-10-02 | Journey signals | Clarified how sentiment is used as a journey signal | Signals should be explained as supporting evidence rather than treated as unquestionable truth | Day 6: clarify sentiment journey signals |
| 7 | 2026-10-03 | Data integrity | Clarified that demo records are synthetic | Synthetic data is suitable for product demonstration but not evidence of real customer behaviour | Day 7: clarify synthetic demo data handling |
| 8 | 2026-10-04 | Health check | Added a health-endpoint check | A simple health check helps verify that the service is available before deeper testing | Day 8: add health endpoint check |
| 10 | 2026-10-05 | Agent workflow | Added a test for agent case-list filtering | Filters that affect day-to-day workflow should be covered by regression tests | Day 10: test agent case list filtering |
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

| 22 | 2026-10-18 | Login safety review | Added a regression test for protocol-relative login return paths | A path starting with two slashes can be interpreted as an external destination and must not be trusted after login | Day 22: test protocol-relative login redirect rejection |

| 23 | 2026-10-19 | Login safety | Rejected control characters in login return paths and added a regression test | Even internal-looking redirect values should not contain line breaks or other control characters | Day 23: reject control characters in login return paths |

| 24 | 2026-10-20 | Session security | Added a production-mode test confirming login cookies include HttpOnly, Secure, and SameSite=Lax flags | Authentication is safer when session-cookie protections are enforced and covered by regression tests | Day 24: test production session cookie security |

| 25 | 2026-10-21 | Session security | Added a production-mode logout test confirming that signing out redirects to login and protected pages require authentication again | Logout is only complete when the session is actually cleared and protected pages become inaccessible | Day 25: test production logout session ending |

| 26 | 2026-10-22 | Session security | Added a regression test confirming logout expires the session cookie with Max-Age=0 | Logout should invalidate the browser session cookie, not only redirect the user away from a protected page | Day 26: test logout cookie expiry |

| 27 | 2026-10-23 | Session security | Added a production-mode regression test confirming that a failed login does not issue a session cookie | Authentication failures should not create browser session state | Day 27: test failed login session safety |

| 28 | 2026-10-24 | Login reliability | Added a production-mode regression test confirming login normalizes email case and surrounding spaces | Authentication should accept equivalent email input without weakening password checks or session controls | Day 28: test normalized login email |

| 29 | 2026-10-25 | Authentication safety | Added a production-mode regression test confirming inactive users cannot create a session even with the correct password | Account status must be enforced as part of authentication, not only password verification | Day 29: test inactive user login rejection |

| 30 | 2026-10-26 | Authentication safety | Added a production-mode regression test confirming an already logged-in user loses access once the account becomes inactive | Session checks should enforce current account status on every protected request, not only at login time | Day 30: test inactive session rejection |

| 31 | 2026-10-27 | Queue clarity | Showed a separate promise state when no commitment is recorded and covered it with a focused render test | A missing promise is different from a promise that was fulfilled, so the risk queue must not label both as met | Day 31: distinguish missing promises from met promises |

| 32 | 2026-10-28 | Queue clarity | Showed the number of missed commitments in the high-risk queue and covered it with a focused render test | Managers can judge the scale of a broken commitment before opening a case | Day 32: show missed commitment count |

| 33 | 2026-10-29 | Analytics accuracy | Corrected silent-wait calculation for unresolved cases so ongoing silence continues to the current time and added a regression test | A live support metric should keep measuring the customer's current wait instead of stopping at the last stored interaction | Day 33: correct unresolved silent wait |

## Historical numbering note

The early Git history contains a numbering gap: no verified `Day 9` commit was found during the repository audit, and an earlier `Day 11: test transfer effort scoring` commit exists on 2026-10-06 while the progress log already used Day 11 for the 2026-10-07 follow-up-ownership work. This log does not invent or renumber historical work. The inconsistency is documented here and future day numbering should remain consistent from the current sequence onward.

## Notes format

Keep each note short and honest:

- What business problem did this touch?
- Which part of the project did it involve?
- Which tool, language, or framework did it help you understand?
- How would you explain it in an interview?
