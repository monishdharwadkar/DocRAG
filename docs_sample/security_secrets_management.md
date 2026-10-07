# Secrets Management & HashiCorp Vault Policy

## Zero Plaintext Secrets Rule
- Plaintext passwords, API keys, private keys, or tokens must NEVER be committed to Git repositories.
- Use `gitleaks` pre-commit hooks to automatically scan commits for credentials.

## HashiCorp Vault Integration
- Secrets are dynamically injected into Kubernetes pods via Vault Agent Sidecar Injector.
- Application pods authenticate with Vault using Kubernetes ServiceAccount JWT tokens.
- Secret paths follow standard convention: `secret/data/environment/service-name`.
