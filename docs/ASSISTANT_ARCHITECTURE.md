# CX Intelligence Assistant

The free baseline assistant is not a generic chatbot. It accepts bounded questions about a selected CarePulse case or the current dataset, reads calculated risk, Silent Wait, Customer Effort, recommendations, and overview metrics, and returns an evidence-backed response. Unsupported questions are declined instead of answered from imagination.

The implementation is `src/assistant.py`, the page is `/assistant`, and the optional event simulator is `/simulator`. A future production assistant could use a local retrieval system over approved methodology documents, but the source of truth should remain the database and calculation engines.

