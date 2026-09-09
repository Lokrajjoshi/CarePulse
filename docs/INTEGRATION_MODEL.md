# Integration model

CarePulse should consume approved internal events from chat, email, voice-transcript, CRM, ticketing, and survey systems through webhooks, REST APIs, scheduled exports, or event streams. The prototype's `POST /api/events` endpoint and `/simulator` page demonstrate this contract with synthetic data. No manual copying of entire conversations is required, and the private deployment can process metadata or redacted/local text according to policy.

