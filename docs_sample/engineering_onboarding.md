# Engineering Onboarding & Setup Guide

## Welcome to Engineering
This guide covers everything required to set up your local development environment and gain access to internal tools.

## Prerequisites & Account Setup
1. **GitHub Enterprise**: Request access to the main organization from your engineering manager.
2. **Okta Single Sign-On**: Enable 2FA using hardware security key (YubiKey) or Okta Verify.
3. **VPN Access**: Install WireGuard VPN client and download cluster credentials from internal portal.

## Local Development Requirements
- **Docker Desktop / Colima**: Required for running Postgres, Redis, and local services.
- **Python**: Python 3.11+ required for backend services.
- **Node.js**: Node 18+ required for frontend React applications.
- **Pre-commit Hooks**: Install pre-commit hooks via `pre-commit install` to run black, ruff, and ESLint automatically before pushing code.
