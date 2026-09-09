# Public Demo Guidance

CarePulse is intentionally local-first. The full application runs at zero cost on a Windows laptop with Python, SQLite, and open-source packages. No public URL is claimed by this project.

For an interview or review, use one of these free-safe options:

1. Run locally and share your screen.
2. Connect the reviewer to the same Wi-Fi and share the laptop's local IPv4 URL, after allowing Python through Windows Firewall if prompted.
3. Use a temporary tunnel only if you understand its privacy implications and the provider currently offers a no-billing path. Never upload real customer conversations.

For a permanent internet deployment, an organisation should provision its own approved infrastructure and security controls. Provider free tiers and billing policies change, so this repository does not silently select a host or request a card.

## Optional free portfolio deployment

The repository includes `render.yaml` for a Render Free web service. Render's current documentation says Free web services can host Python applications, but they sleep after 15 minutes idle, use ephemeral local files, and are not intended for production. The SQLite demo database can reset after a restart or redeploy. Use synthetic data only, select the Free plan, and verify that no payment method or paid upgrade is enabled.

The repository pins Python 3.12 in `.python-version` for deployment compatibility with the pinned SQLAlchemy and scientific Python packages.
