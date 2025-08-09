---
layout: post
title:  "Practice and Architecture Analysis of Integrating a Web Application Firewall (WAF) into a Kubernetes Cluster"
date:   2025-08-09
categories: jekyll update
tags: 
  - Kubernates
  - WAF
  - Security 
lang: en
---

{% include lang-switch.html %}

By integrating a Web Application Firewall (WAF) into a Kubernetes cluster, malicious traffic entering the cluster can be filtered to protect publicly exposed services (such as reverse proxies, API gateways, and content management systems). This prevents attacks such as path traversal, Remote Code Execution (RCE), web crawling, credential scanning, and Denial of Service (DoS), reduces backend resource consumption, and enhances overall security.  
This article uses **Wallarm WAF** as an example, but the approach applies to other WAF products as well (such as AWS WAF, Cloudflare WAF, ModSecurity, and F5 Advanced WAF).

---

## Architecture and Component Responsibilities

### 1. External Services (Provided by Wallarm)
- **WAF API/Dashboard**: Hosted on the WAF provider’s cloud, used to visualize attack data, traffic statistics, and request details.
- **Node Management**: A node in the dashboard corresponds to a WAF Ingress Controller instance inside the cluster. Each node is assigned a unique token at creation, used to securely link the cluster with the dashboard.
- **WAF Rule and Detection Engine**: Identifies malicious requests in real time based on built-in rules (e.g., sensitive file access, SQL injection, XSS).

### 2. User Infrastructure
- **ELB (Elastic Load Balancer)**: Public entry point that forwards traffic to the Ingress Controller in the cluster.
- **Managed Kubernetes Cluster (e.g., EKS, AKS, GKE)**: Hosts protected workloads and the Ingress Controller. Managed by the cloud provider, ensuring high availability, automatic upgrades, and infrastructure maintenance.
- **Image Registry (ECR, GCR, ACR, etc.)**: Stores custom-built WAF Ingress Controller images (based on the official NGINX Ingress Controller or other ingress implementations).

### 3. Internal Kubernetes Resources
- **WAF Ingress Controller**: A customized ingress controller image with the WAF module built in, providing security detection and blocking capabilities.
- **Data Collection Component (e.g., Wstore)**: Deployed alongside the Ingress Controller to gather traffic metadata and send it to the WAF API.
- **Protected Ingress Resources**: Ingress resources configured with annotations to enable WAF detection and blocking.
- **Application Workloads**: Backend services exposed to users (e.g., API services, web frontends, file download services).

![kubernetes-waf-integration-architecture]({{ '/assets/images/post_img/kubernetes_waf_integration_architecture.png' | relative_url }})

---

## Traffic Flow

1. External traffic reaches the ELB (or another load balancer).
2. The ELB forwards the traffic to the **WAF Ingress Controller** inside the cluster.
3. The WAF module analyzes each request in real time:
   - Malicious traffic → Returns `403 Forbidden` immediately and does not reach backend services.
   - Legitimate traffic → Forwards to backend applications.
4. The data collection component (e.g., Wstore) gathers analysis data and sends it to the WAF Dashboard.
5. The dashboard displays attack sources, types, timestamps, IP addresses, CVE details, and other visualized metrics.

---

## Deployment and Configuration Steps
> Example given with Wallarm; other WAF products may use an Operator, YAML manifests, edge proxies, or cloud-based services.

1. **Obtain the Helm Chart** and extract the default `values.yaml`.
2. **Customize key configurations**:
   - `enabled: true`
   - `token`: Node token obtained from the dashboard
   - `apiHost`: WAF API endpoint (e.g., `us1.api.wallarm.com`, independent of cluster location)
   - `nodeGroup`: Corresponds to the node group name in the dashboard
3. **Upgrade the Ingress Controller**:
   - Upgrade to a WAF-compatible version (e.g., NGINX Ingress Controller 1.11.5) and address security vulnerabilities in older versions.
4. **Configure annotations for protection mode**:
   - `nginx.ingress.kubernetes.io/wallarm-mode: block` (blocking mode, default is `monitoring` which only observes)
   - `nginx.ingress.kubernetes.io/wallarm-application: <integer ID>` (distinguishes applications/environments)
5. **Deploy the image**:
   - Build a custom image from the official base and push it to a private image registry.
6. **Secure token management**:
   - Configure via scripts or secure secret management systems (e.g., KMS, Secrets Manager, Sealed Secrets) to avoid plain-text exposure.

---

## Traffic Control and Differentiation Strategies

- **Application ID Uniqueness**:  
  Different ingress resources/environments should use different IDs to avoid data mixing. Behavior for “same ID across environments” still needs verification.
- **Node and Token Management** (two common approaches):  
  - **Separate Node+Token per environment**: Strong isolation, easier access control and monitoring separation.  
  - **Single Node + Multiple Application IDs**: Simplifies management but requires strict avoidance of ID conflicts.
- **IP Whitelisting and Rate Limiting**:  
  For endpoints like health checks or version queries that may be accessed frequently, configure IP whitelists or rate limiting at the ingress controller level. These are general ingress features, not WAF-specific.

---

## Monitoring and Validation

- **Functional Tests**:
  - Malicious request `GET /etc/passwd` → Blocked with `403`
  - Legitimate request (e.g., `/version`) → Successfully processed
- **Dashboard Visualization**:
  - Total requests and request rate
  - Malicious request details: type, CVE, source IP, domain, target path
  - Traffic view segmented by Application ID
- **Use of Attack Source Information**:
  - Source IPs can be used for further blocking or allowlisting at the load balancer or firewall level.

---

## Integration Considerations and Challenges

1. **Conflict with Existing Deployment Processes**:  
   - Some automation may overwrite an existing **Ingress Controller** (adjust `ingressClassName` or deployment logic to avoid replacement during upgrades/redeployments).
2. **Non-WAF Scenarios**:  
   - Even services protected by VPN and application-level tokens should be monitored for potential bot traffic; ingress-level rate limiting or ACLs may still be needed.
3. **Licensing and Costs**:  
   - Confirm the billing model (per application, per traffic volume, per ruleset, etc.); providers vary in restrictions and pricing tiers.
4. **Ensuring Availability of Legitimate Requests**:  
   - Configure rate limits or circuit breakers for endpoints prone to abuse to avoid backend resource exhaustion.
5. **Multi-Environment/Multi-Cluster Consistency**:  
   - Ensure ingress controllers are deployed and configured in each environment/cluster; can connect to a single WAF API or be separated by environment.
