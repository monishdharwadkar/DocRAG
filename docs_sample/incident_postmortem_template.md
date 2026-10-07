# Incident Postmortem & Severity Guidelines

## Severity Levels
- **SEV-0**: Total outage affecting core revenue-generating systems. SLA breach imminent. Required response time: < 5 minutes.
- **SEV-1**: Major feature degradation affecting > 25% of users without immediate workaround. Required response time: < 15 minutes.
- **SEV-2**: Moderate issue with workaround available, or affecting single non-critical service. Required response time: < 1 hour.
- **SEV-3**: Minor bug or cosmetic defect. Addressed during standard sprint planning.

## Postmortem Workflow
1. **Incident Resolution**: Resolve incident and stabilize primary infrastructure.
2. **Drafting Timeline**: Within 24 hours of incident resolution, the Incident Commander drafts the postmortem document.
3. **Five Whys Analysis**: Perform root cause analysis using the 5-Whys methodology.
4. **Action Items**: Assign clear ownership and ticket IDs for all preventive action items.
5. **Review Meeting**: Schedule postmortem review with engineering leadership within 3 business days.
