# 🔐 Security Policy

Thank you for taking the time to help secure B-Vista. We take the privacy and integrity of data seriously, especially since B-Vista is often used with sensitive datasets.

---

## 📆 Supported Versions

Only the latest major or minor release of B-Vista receives security updates:

| Version | Supported | Notes                        |
|---------|-----------|------------------------------|
| 0.1.x   | ✅ Yes     | Actively maintained (dev)    |
| < 0.1   | ❌ No      | Pre-release or deprecated    |

---

## 🛡️ Threat Model & Surface Area

### ✋ What B-Vista **does not** do:
- It **does not expose** public ports unless you explicitly run it that way.
- It **does not store** your data persistently.
- It **does not send** your data to external servers or APIs (unless you call one explicitly).

### ✅ What B-Vista **does** to secure your usage:
- Session-based isolation of uploaded DataFrames.
- Temporary files stored in private directories, deleted on session expiry.
- Inactivity-based session auto-expiration (default: 60 minutes).
- WebSocket messages scoped to session ID and validated for structure and type.
- No unfiltered eval/exec operations on uploaded or ingested data.

---

## 🔐 Recommended Deployment Practices

If you're deploying B-Vista in a team or production setting, we recommend:

- **Use HTTPS** (via reverse proxy: NGINX, Caddy, or similar)
- **Run behind authentication** (basic auth, token, or header-based)
- **Deploy with Docker or similar containers** to isolate dependencies
- **Avoid shared ports** unless protected via VPN or gateway
- **Set strict environment variables** to disable dev tools (`FLASK_ENV=production`, `DEBUG=0`)

---

## 📣 Reporting a Vulnerability

If you discover a security issue in B-Vista:

- 📧 **Email us privately** 
- Or contact the maintainers directly via GitHub
- Please **do not file public GitHub issues** for security concerns

We will:
1. Acknowledge your report within 48 hours
2. Investigate and verify the issue
3. Release a patch or workaround ASAP
4. Credit your responsible disclosure if desired

---

## 🧠 Responsible Disclosure

We deeply appreciate the community’s help in keeping B-Vista safe and open.

All disclosed vulnerabilities will be documented (if public) in a `SECURITY_ADVISORIES.md` file or GitHub’s built-in advisories, along with mitigation steps.

---

## 🤝 Thanks

Thanks for helping us build a safer open-source ecosystem.  
Secure software is only possible with a secure community 💙

—
The B-Vista Maintainers
