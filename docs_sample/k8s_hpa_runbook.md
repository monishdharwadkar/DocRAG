# Kubernetes Horizontal Pod Autoscaling (HPA) Runbook

## Overview
Horizontal Pod Autoscaler (HPA) automatically adjusts the number of replica pods in a deployment based on CPU utilization, memory usage, or custom Prometheus metrics.

## HPA Configuration Parameters
- **Target CPU Utilization**: Default threshold is set to 75% across all running replicas.
- **Target Memory Utilization**: Default threshold is set to 80% of configured container memory limits.
- **Scale Down Stabilization Window**: Set to 300 seconds (5 minutes) to prevent flapping during momentary traffic dips.
- **Scale Up Stabilization Window**: Set to 0 seconds for rapid reaction to sudden load spikes.
- **Min Replicas**: Minimum 3 pods across distinct availability zones.
- **Max Replicas**: Maximum 50 pods per service deployment.

## Troubleshooting High CPU & OOMKilled Alerts
1. Check pod status using `kubectl get pods -l app=service-name`.
2. Inspect describe output for OOMKilled events: `kubectl describe pod <pod-name>`.
3. Check HPA status and current metric values: `kubectl get hpa <deployment-name>`.
4. If HPA reaches `Max Replicas` (50), evaluate if cluster node pool autoscaling is enabled in GCP/AWS.
5. In case of emergency traffic overload, manually scale up deployment using `kubectl scale deployment <deployment-name> --replicas=30`.
