---
layout: post
title:  "Deep Dive into Load Balancer Orchestration: Reconcile, High Availability, and Elastic Scaling"
date:   2025-08-24
categories: jekyll update
tags: 
  - Kubernates
  - ELB
  - Cloud
  - AutoScaling
  - HighAvailability
lang: en
published: false
---

{% include lang-switch.html %}

As cloud providers increasingly focus on performance metrics, **Elastic Load Balancing (ELB)** with auto-scaling capability has become a critical part of highly available architectures. ELB not only distributes traffic but also **must scale and self-heal itself** to handle sudden load spikes and node failures.

This article explores the **orchestration logic**, **high availability (HA) mechanisms**, and **LBVM (Load Balancer Virtual Machine) auto-scaling process** behind ELB, showing how “declarative configuration + continuous reconciliation” ensures a stable and elastic service entry point.

> 💡 **Note**: This article focuses on the **self-managed load balancer** paradigm—where the control plane manages LBVMs, ENIs, DNS, and related resources. This shares the same architectural philosophy as managed ELBs (AWS/GCP/Azure) but provides more engineering transparency, suitable for private or hybrid cloud gateway systems.

---

## 1. ELB Basics and Types

**Core responsibilities**:
- Automatically distribute incoming traffic to multiple backend targets;
- Perform health checks and only route to healthy instances;
- Dynamically scale its own capacity based on traffic load;
- Integrate with WAF (Web Application Firewall) in L7 mode for security.

### Three Main Types

| Type | Layer | Characteristics |
|------|-------|-----------------|
| **CLB (Classic Load Balancer)** | L4/L7 | Early form, basic functionality |
| **ALB (Application Load Balancer)** | L7 | Advanced routing (path, hostname) |
| **NLB (Network Load Balancer)** | L4 | High-performance, low-latency TCP/UDP |

> This article focuses on **CLB and ALB orchestration and scaling mechanisms**, which can be generalized to gateways, proxies, and edge routing systems.

---

## 2. Orchestration Workflow: From Request to Ready Instance

### 2.1 Creation Workflow Overview

When a user requests a new ELB, the system validates resources, generates configurations, launches instances, and registers services. This process involves **API Server** and **Orchestrator** working together.

#### Workflow steps:

1. **User Request** → Create Load Balancer.
2. **API Server Validation**:
   - IAM authorization check;
   - Call EC2 API to validate VPCs and subnets;
   - If TLS is enabled, validate certificates;
   - Generate ELB **Spec (Desired State)**.
3. **Orchestrator Orchestration**:
   - Periodically fetch Spec;
   - Render Proxy/WAF and Agent configuration;
   - Create ENIs and launch LBVMs;
   - Create WAF/certificate resources if enabled.
4. **LBVM Startup**:
   - Agent sends heartbeat;
   - Orchestrator confirms health and registers DNS or adds to target pool;
   - LBVM starts reporting metrics (CPU, connections, memory).
5. Orchestrator continuously collects metrics to drive scaling decisions.

---

### 2.2 Traffic Ingress Models

In production, two common patterns exist:

#### Method 1: Per-Instance DNS Registration (simple but flawed)

- Each LBVM gets a DNS record;
- When an instance is added, its DNS is published; when removed, the record is deleted.

![Per-Instance DNS Registration]({{ '/assets/images/post_img/elb_dns_registration.png' | relative_url }})

> ⚠️ **Problem**: DNS caching and TTL jitter can cause request instability, especially during frequent scaling, resulting in errors like *502 Bad Gateway*.

#### Method 2: Stable Entry + Dynamic Target Pool (recommended)

- Clients connect via a **stable entry** (VIP, Anycast IP, NLB/GSLB frontend);
- LBVMs dynamically register/deregister from the target pool;
- DNS maintains only the entry, not individual LBVM records.

**Advantages**:
- Avoids DNS jitter and cache inconsistency;
- Matches practices in AWS ELB, GCP LB, and Envoy/NGINX;
- Simplifies multi-AZ HA and load balancing.

![Dynamic_Target_Pool]({{ '/assets/images/post_img/elb_dynamic_target_pool.png' | relative_url }})

> 🔧 **Engineering Tip**: Prefer the “stable entry + pool” design to decouple DNS resolution from instance lifecycle.

---

### 2.3 LBVM Internal Components

Regardless of ingress mode, each LBVM generally contains:

| Component | Role |
|-----------|------|
| **Agent** | Control-plane component that renders configs for Proxy/WAF, handles heartbeats |
| **Proxy** | Actual data-plane traffic handler (Nginx, HAProxy, Envoy) |
| **WAF Module** | L7 security layer (SQL injection, XSS detection) |

> ✅ The Agent is the bridge between control and data planes, enabling config hot reload, heartbeat reporting, and health feedback.

---

## 3. Desired State / Snapshot / Reconcile

Modern cloud-native systems follow **“declarative + eventual consistency”** models, centered on the **Reconcile Loop**.

### Key Concepts

| Concept | Definition |
|---------|------------|
| **Desired State** | User-defined Spec: AMI, instance type, min/max LBVMs, TLS certs, WAF config |
| **Snapshot State** | Actual runtime state: running instances, ENIs, DNS, SGs, certs |
| **Reconcile** | Orchestrator continuously compares Desired vs. Snapshot, then issues corrective actions |

### Workflow

- **Polling + Event-driven triggers** keep states aligned;
- **Sync Jobs** (via Temporal or job queues) perform async corrective actions;
- **Job types**: launch/terminate LBVMs, update DNS, ENIs, certs, WAF;
- **Idempotency** ensures retries converge to the same result;
- **Zero-disruption updates**:  
  - New LBVM passes health check before DNS registration;  
  - Old LBVM is deregistered only after **Draining**.

![ELB Reconcile]({{ '/assets/images/post_img/elb_reconcile.png' | relative_url }})

> ✅ This “detect diff → generate job → async reconcile” design underpins Kubernetes Operators, Terraform, and ArgoCD.

---

## 4. LBVM Lifecycle & HA Mechanisms

### State Machine

```text
Launching → Pending → Routable → Draining → Terminated
                     ↓
                 Unroutable
```

**LBVM (Load Balancer Virtual Machine)** = VM that runs proxy + WAF.

**States**:
- **Launching** → Instance requested;
- **Pending** → Waiting for heartbeat;
- **Routable** → Heartbeat healthy, DNS registered / pool joined;
- **Unroutable** → Heartbeat lost, DNS deregistered;
- **Draining** → Stop new connections, allow existing ones to complete;
- **Terminated** → Shut down.

### Mechanisms

- **Heartbeat loss = DNS deregistration**: prevents routing to unhealthy nodes.  
- **Draining** ensures smooth disconnect for long-lived sessions.

In production, Draining is more engineered:  
- **Dual-threshold strategy**: Deregister from entry, wait until connections < threshold or timeout, then terminate.  
- **Protocol details**:  
  - L4: Handle TCP FIN, half-close, TIME_WAIT.  
  - L7: Impose max lifetime for WebSocket/HTTP2, graceful close.  
- **Rollback**: Rolling updates define  
  - **maxUnavailable** (down limit)  
  - **maxSurge** (up limit)  
  If failures occur, rollback automatically for zero downtime.  

**HA (High Availability)**:  
- **Pending Timeout**: no heartbeat during startup → replace.  
- **Unhealthy Timeout**: loss of heartbeat → deregister + replace.  
- Any state outside Desired triggers reconciliation.  

---

## 5. Auto Scaling Logic

### Basic Mechanism

- **Metrics**: CPU, connection count, memory usage.  
- **Subnet-level averages** used for scaling decisions.  
- **Voting**:
  - > Scale-out threshold → +1  
  - < Scale-in threshold → -1  
  - Within band → 0  
- **Final decision**:  
  - Any metric +1 → add 1 LBVM  
  - All metrics -1 → remove 1 LBVM  
- **Cooldown**: 10 min to avoid flapping.  
- **Scale-in policy**: random instance selection.  
- **Warming**: Admin Flags pre-inject LBVMs ahead of traffic spikes.  

### Example

| Metric | Value | Threshold | Vote |
|--------|-------|-----------|------|
| CPU | 85% | >80% → scale-out | +1 |
| Memory | 35% | <40% → scale-in | -1 |
| **Decision** | | | **+1 instance** |

---

### Advanced Improvements

The “vote by threshold” approach is simple but can flap. Production optimizations include:

| Enhancement | Description |
|-------------|-------------|
| **Target Tracking** | Set per-instance target (e.g., 1500 connections), adjust proportionally |
| **Hysteresis** | Stagger scale-out vs. scale-in thresholds |
| **Step Scaling** | Larger breaches trigger larger scaling increments |
| **Weighted Priorities** | Connections > CPU > memory, or time-based weights |
| **Per-AZ evaluation** | Ensure balanced scaling across AZs |
| **Safeguards** | Minimum pool size to prevent over-aggressive scale-in |

---

### Rolling Replacement & Warming Enhancements

Beyond Admin Flags:  
- **Canary rollout**: small subset of LBVMs get traffic first; expand if stable.  
- **Concurrency caps**: limit simultaneous replacements.  
- **Warm Pools**: maintain pre-warmed LBVMs for fast scale-out.  
- **Config preloading**: push configs before traffic cutover.  

---

## 6. External Resource Consistency & Garbage Collection

### Problem

Failures may create “zombie resources”:  
- EC2 instance exists but untracked;  
- ENI/EIP/DNS not cleaned up;  
- SG rules lingering.  

These waste cost and pose risks.

### Solutions

- **Consistency checker**: compare Snapshot vs. actual resources;  
- **Diff detection**: flag orphaned resources;  
- **Alerts**: trigger notifications when mismatch found.  

### Garbage Collection Strategies

| Strategy | Description |
|----------|-------------|
| **Manual** (current) | Safe, avoids accidental deletion |
| **Mark & Sweep** | Periodically mark live resources; unmarked → quarantine, then delete |
| **Owner Tags** | Resources tagged for exclusive controller ownership |
| **Protected Windows** | Only GC in low-traffic windows |
| **Change Audit** | Log deletions for traceability |

> ✅ Tip: Start with detect+alert+manual cleanup, progress gradually to automated GC.

---

## 7. Control Plane Engineering: Operator Model

ELB orchestration resembles a **custom controller** and can adopt Kubernetes Operator practices:

| Feature | Description |
|---------|-------------|
| **CRD + Controller** | Declarative state, reconciliation loop |
| **Work Queue + Backoff** | Handle jitter, recover gracefully |
| **Finalizers** | Ensure orderly cleanup (ENI, DNS, EIP) |
| **Leader Election** | HA for orchestrators |
| **Sharding/Lease** | Horizontal scalability |
| **Idempotency Keys** | Avoid duplicate resource creation |

> 🛠️ Best practice: design ELB orchestrator as an Operator for maintainability & observability.

---

## 8. Scaling + HA + Reconcile Architecture Diagram

![ELB orchestrator]({{ '/assets/images/post_img/elb_orchestrator.png' | relative_url }})

> 📌 Caption: Illustrates the complete loop from user request to automatic scaling.

---

## 9. Summary

**Three core mechanisms**:

| Mechanism | Description |
|-----------|-------------|
| **Reconcile** | Align Desired vs. Actual state via eventual consistency |
| **HA** | Heartbeats + timeouts + draining = seamless recovery |
| **Scaling** | Multi-metric voting + cooldown, with warming & rolling upgrades |

**Reusable for**:  
- Any pool-based service: API gateways, message queues, cache clusters, edge nodes.  
- Characteristics: independent instances, health checks, dynamic routing.  

**Universal Value**:  
- Matches principles of AWS ELB, GCP LB, K8s Ingress Controllers.  
- Differ in orchestration, heartbeat, and scaling details.

---

## 10. Broader View: The Philosophy of Reconcile — From Systems to Cognition

In distributed systems, **Reconcile** means continuously comparing Desired vs. Actual states and eliminating differences until consistency is achieved.

But this principle also applies in **human-AI collaboration**.

### The Human-AI Misalignment Problem

Imagine:  
A robot plans a detour instead of the shortest path.  
Humans think: “Why not the straight line? Is it broken?”

The truth: **The straight path is blocked**, which the robot knows but the human doesn’t.  

The issue: **AI model (A) ≠ Human model (H)**.  
If AI just says “this is optimal,” humans won’t buy it.  
The fix: **AI must explain why**, i.e., **align human model with AI’s model**.

### Paper Insight: Model Reconciliation

In *[Plan Explanations as Model Reconciliation](https://arxiv.org/abs/1701.08317)*:  
> **Explanations are not about repeating the plan, but reducing the gap between human and AI models.**

This process = **Model Reconciliation**.  
Goal: humans update their mental model H → H’ to match AI model A, building trust.

### Analogy: System vs. Cognitive Reconcile

| Dimension | System Reconcile (K8s) | Cognitive Reconcile (Human-AI) |
|-----------|--------------------------|--------------------------------|
| **Desired State** | User-declared Spec (replicas=3) | AI’s full knowledge (A) |
| **Actual State** | Current Snapshot | Human mental model (H) |
| **Diff Detection** | Compare Desired vs. Actual | Compare A vs. H |
| **Correction** | Launch/terminate/update | Explanation (e.g., “path is blocked”) |
| **Execution** | Automated Sync Jobs | Language, visualization, demonstration |
| **Goal** | State consistency | Shared understanding |

![Cognitive Reconcile]({{ '/assets/images/post_img/cognitive_reconcile.png' | relative_url }})

### Example

- **Scenario**: Robot must pass a room.  
- **AI Model A**: knows main door is locked.  
- **Human Model H**: assumes main door is open.  
- **Plan P**: detour via side door.  
- **Human confusion**: “Why detour?”  
- **Explanation E**: “Main door is locked.”  
- **Result**: Human updates H → H’, accepts plan.  

This is **cognitive Reconcile**.

### Why This Matters

It shows a universal principle:  
> **Reconcile = eliminate inconsistency, build trust.**

- Systems: control loops fix drift;  
- Human-AI: explanations fix misunderstandings.  

Both pursue **consistency** — one in machine state, one in human cognition.

### Engineering Implications

- **Automation must be explainable**: not just “what” but “why.”  
- **Alerts/logs should highlight diffs**: show gaps between user expectation and system reality.  
- **CI/CD failures**: explain expected vs. actual outcomes.  

> 🔁 Reconcile is both a **self-healing mechanism for systems** and a **trust-building mechanism for humans**.

---

## Conclusion

ELB orchestration is a concrete case of **Declarative Control + Reconcile**:

- Declare what you want (Desired State);  
- Continuously detect drift;  
- Apply corrective actions;  
- Reach consistency.  

This ensures HA and elastic scaling, embodying the cloud-native ethos: **systems manage themselves**.  

Extending to human-AI collaboration:  
**Reconcile evolves from system alignment to cognitive alignment**.  
It is not just a technical loop, but a philosophy of building **trustworthy automation**.

Future systems, whether load balancers or AI agents, share the same ultimate mission:  
**In a complex world, continuously reconcile, stay consistent, and remain reliable.**
