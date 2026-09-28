# Repository engineering rules

- Preserve the published ethylene, oxygen, carbon-dioxide, perforation, respiration, scavenger, and time-step equations unless explicitly requested.
- Keep request work bounded and avoid external services, polling, or retained simulation data.
- Never commit email logs, credentials, generated plots, or user inputs. Email records are host data and must be minimally handled.
- Keep the responsive single-page form and plot workflow backward compatible.
- Follow `docs/CHANGE_SAFETY_CONTRACT.md` and `docs/DEPLOYMENT_AND_ROLLBACK.md`. `main` is the only release branch and GitHub Actions are intentionally not used.
