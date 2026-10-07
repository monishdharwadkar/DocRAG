# GitHub Actions CI/CD & K8s Deployment Workflow

## CI Pipeline Stages
1. **Linting & Formatting**: Runs `ruff`, `black`, and `tsc` on all pull requests.
2. **Security Vulnerability Scanning**: Scans container images using Trivy.
3. **Automated Unit & Integration Testing**: Requires > 80% coverage to allow merging.

## Deployment Pipeline (ArgoCD)
- Continuous deployment to staging environment occurs automatically on merge to `main`.
- Production deployment requires manual approval in Slack channel `#release-approvals`.
- ArgoCD sync policy uses automated rollbacks if health checks fail within 3 minutes of deployment.
