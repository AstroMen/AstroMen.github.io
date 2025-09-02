---
layout: post
title:  "SAFE-MCP Community Recap: Building a Security Baseline for AI Agents"
date:   2025-09-02
categories: jekyll update
tags: 
  - Security
  - Model Context Protocol
  - AI Agent
lang: en
---

> From Multi-modal Prompt Injection to Agent CLI Exploitation, from Non-Human Identity to Decentralized Trust — a deep dive into MCP security in practice

## 📌 TL;DR: Quick Take on SAFE-MCP

- **SAFE-MCP** is an **open-source security framework** designed to build an actionable security baseline for the **Model Context Protocol (MCP)**, helping enterprises and developers systematically defend against AI Agent risks.
- It adopts a **MITRE ATT&CK-style taxonomy**, assigning unique IDs (e.g., `SAFE-T1001`) to each MCP attack (Prompt Injection, OAuth abuse, Agent Chain attacks), enabling standardized naming and cross-team communication.
- All security entries are based on **real-world attack cases**, including:
  - **Multi-modal Prompt Injection** (instructions hidden in images/audio)
  - **Agent CLI Weaponization** (malicious NPM packages stealing SSH keys and crypto wallets)
  - **Vector Database Poisoning** (covert prompt injection in RAG systems)
  - **OAuth token abuse and missing audience validation**
- Driving collaboration with **OIDC AI Identity WG, Linux Foundation OpenSSF, OWASP**, aiming to evolve SAFE-MCP into an industry-wide security standard.
- Provides a **vulnerability sandbox with reproducible attack scenarios**, supporting hackathons and security training.
- Encourages community contributions: developers can submit techniques, mitigations, or tool integrations to become co-authors of the standard.
- The ultimate goal: Enable CISOs and engineers to confidently answer—**“Is your MCP system SAFE-MCP compliant?”**

---

## 🔍 What is SAFE-MCP? More Than a Guide—It’s a “Security Language”

**SAFE-MCP** (Secure Model Context Protocol) is an **open-source security framework** created to provide an actionable evaluation and defense system for **Anthropic’s Model Context Protocol (MCP)**.

Its origin comes from a real-world problem:  
> When a CISO is asked, “Can we safely deploy MCP?”, they have no authoritative security baseline to rely on.

SAFE-MCP aims to become that **checklist you can tick off**—  
just like you reference the OWASP Top 10 for web services, or NIST SP 800-204D for cloud-native systems, in the future you will ask:

> “Is it SAFE-MCP compliant?”

👉 **GitHub**: [https://github.com/SAFE-MCP/safe-mcp](https://github.com/SAFE-MCP/safe-mcp)  

### 🧩 Three Core Design Principles

#### 1. **Modeled after MITRE ATT&CK, Building a Taxonomy of Attacks**
SAFE-MCP models MCP threats in three layers:
- **Tactics**: The attacker’s goals, such as privilege escalation or data exfiltration  
- **Techniques**: The concrete methods, such as Prompt Injection or OAuth token abuse  
- **Evidence**: Real-world incidents and forensic indicators  

This structure shifts security teams from vague concerns to specific defenses.

#### 2. **Defining a “Security Vocabulary”: Unified Language for Engineers**
Each attack is assigned a unique ID, for example:
- `SAFE-T1001`: MCP Rug Pull Attack (server changes instructions post-authorization)
- `SAFE-T2001`: Multi-modal Prompt Injection (malicious instructions in images/audio)
- `SAFE-T3001`: Agent CLI Weaponization (developer CLI exploited via malicious packages)

Like HTTP 404 or CVE IDs, this makes communication faster and more precise.

#### 3. **Grounded in Real Attacks, Not Theoretical Models**
Frederick Kautz emphasized:
> “Many developers think MCP attacks are still theoretical, but the reality is we see new reports almost daily—crypto wallets drained, data leaks, systems compromised via prompt injection.”

Every SAFE-MCP entry must include a **real-world case or reproducible PoC** to ensure practical value.

---

## ⚠️ OAuth: “A Simple Protocol with Complex Traps”

The MCP spec looks clean—it defines a JSON interface over SSE. But the real complexity comes from its dependencies: **OAuth and Server-Sent Events (SSE).**

As Frederick noted:
> “MCP itself is ‘easy’ but not ‘simple.’ It pulls in protocols like OAuth, which are extremely complex and disastrous if misused.”

### 🔐 OAuth Best Practices: Two Non-Negotiable Rules

#### ✅ Rule 1: Never Hand-Roll OAuth
- OAuth involves dozens of security edge cases.
- Correct approach: use mature libraries (Auth0, Okta SDK), avoid reinventing the wheel.

#### ✅ Rule 2: Always Validate the `audience` Field
Suppose your MCP service is `acme.example`. When receiving a GitHub token, you must check:
```json
{
  "aud": "acme.example"
}
```

If `aud` is `github.com` or something else, the token was **not issued for you** and must be rejected.  

> 🌪️ Otherwise, attackers could reuse tokens from other MCP services to impersonate users.

Frederick warned:  
> “If I don’t validate audience, an attacker can take a token issued for foo.com and use it against me. The token is valid, but it’s not mine — I must reject it.”

---

## 🧪 New Attack Cases: MCP’s Rapidly Expanding Threat Surface

SAFE-MCP highlights **entirely new attack paths** emerging in the AI Agent ecosystem. Recent PRs captured threats like:

| Attack Type | Description | Mitigation |
|-------------|-------------|------------|
| **Multi-modal Prompt Injection** | Encode malicious instructions in image pixels (e.g., 255,255,254) or audio spectrograms | Semantic input validation, limit contextual injections |
| **Agent CLI Weaponization** | Malicious NPM package executes on install, stealing `.env`, SSH keys, wallets | Disable auto-exec, enforce human code review |
| **Vector DB Poisoning (RAG Attacks)** | Inject prompts into KB, triggered during retrieval | Integrity checks and access controls for RAG sources |
| **Container Escape & Privilege Escalation** | Exploit sandbox tool vulnerabilities to break out to host | Enforce least privilege, strong isolation |
| **Agent Chain MITM** | Alter messages between chained Agents to mislead actions | Secure handshake ensuring trusted sources |
| **Privilege Escalation in Delegation** | Read-only Agent upgraded to read-write+execute mid-chain | Implement privilege chain validation |

These cases show: **MCP risks go far beyond input poisoning — they affect the full AI workflow.**

---

## 🛠️ Identity & Trust Models: From NHI to Decentralized CA

SAFE-MCP also tackles **trust** — how do we know who an Agent is, and what it can do?

### 🔑 Non-Human Identity (NHI)
- Current identity systems (Okta, etc.) are human-centric.  
- AI Agents, scripts, microservices also need identity.  
- Proposal:  
  - Use TPM or cloud TEEs (e.g., AWS Nitro) as trust roots  
  - Issue sub-certificates to Agents  
  - Build traceable, auditable chains  

💡 Example: PayPal could run its own CA, issuing certs for all internal AI Agents.  

### 🌐 Decentralized Trust Models
- Don’t rely on one central CA.  
- Support multi-org, multi-tenant distributed trust.  
- Inspired by Web3: record policies/identities on blockchain or decentralized storage.  

> “Instead of one central CA, PayPal controls its own Agents, another company controls theirs — that’s a sane trust boundary.” — Arjun Subedi

---

## 🧩 MCP in Essence: Not an API Replacement, but a “Bridge”

A frequent question: **How is MCP different from APIs?**  
Answer: **MCP is an API spec purpose-built for LLMs.**

### 🔄 MCP’s Two-phase Interaction Model

1. **Initialization (Schema Registration)**  
   Tool provides JSON Schema describing functions, parameters, return values.  
   Example:  
   &&&json
   {
     "name": "send_email",
     "description": "Send an email to a recipient",
     "parameters": { ... }
   }
   &&&

2. **Invocation (Structured Execution)**  
   - LLM interprets intent → generates schema-compliant JSON  
   - Tool executes → returns structured result  

### ✅ Why MCP?

| Traditional APIs | MCP |
|------------------|-----|
| Manual integration logic | LLM auto-discovers and calls |
| Assumes deterministic caller | Maps fuzzy language to exact fields |
| No unified discovery | Tools auto-exposed via `/tools` |

> “The value of MCP isn’t fewer APIs, but enabling LLMs to call any tool safely and reliably.” — Frederick Kautz

---

## 📚 From Policy to Procedure: SAFE-MCP in Compliance Systems

SAFE-MCP’s philosophy maps neatly to enterprise compliance layers:

| Layer | Example | SAFE-MCP Role |
|-------|---------|---------------|
| **Policy** | “AI systems must prevent data leakage” | Defines high-level security principle |
| **Standard** | MITRE ATT&CK, OWASP AI Top 10 | Maps attack techniques, taxonomy |
| **Procedure** | “How to configure MCP to prevent T1001” | Concrete operational checklist |
| **Guidance** | “Use LangFuse for observability” | Tooling integration advice |

SAFE-MCP is evolving into the **“playbook” of AI security** — bridging “what to do” with “how to do it.”

---

## 🤝 Community & Collaboration: From Project to Standard

- **9 active contributors**, spanning security, AI, and cloud-native domains  
- **10+ merged PRs**, covering OAuth, CLI security, multimodal attacks  
- **Migrated to independent GitHub org** to mark project’s open-source maturity  
- **First attack sandbox released**, with common MCP misconfigurations for testing  
- **Bi-weekly hackathons & contributor meetups** keep momentum high  

### 🌐 Three Key Standards Partnerships
| Org | Collaboration | Impact |
|-----|--------------|--------|
| **OIDC AI Identity WG** | Co-develop MCP identity standards | NHI standardization |
| **Linux Foundation OpenSSF** | Apply for incubation | Resource support, industry endorsement |
| **OWASP** | Align with AI Security Top 10 | Cross-standard mapping |

Frederick:  
> “Our goal isn’t an isolated framework — it’s a **shared language** for AI security.”  

---

## 🧑‍💻 How Developers Can Contribute

SAFE-MCP is **open, transparent, and community-driven.**

### 🚀 Ways to Join
1. **Contribute Techniques**  
   - Browse open `T1xxx` issues on [GitHub](https://github.com/SAFE-MCP/safe-mcp)  
   - Add cases, tactics, evidence, mitigations  

2. **Submit Mitigations**  
   - Suggest defenses for existing attacks (`M1`, `M2`, etc.)  

3. **Build Toolchains**  
   - Auditing, detection, identity mgmt, observability  

4. **Write Docs**  
   - Guides, best practices, onboarding materials  

---

## ✅ Conclusion: The Future of SAFE-MCP

SAFE-MCP is building a **scalable, verifiable, and practical AI Agent security baseline**:

- ✅ **Standardized language**: IDs and definitions unify communication  
- ✅ **Real-world grounded**: based on true cases, reproducible PoCs  
- ✅ **Operationalized**: checklists, sandboxes, integrations  
- ✅ **Ecosystem-driven**: connected to OIDC, OpenSSF, OWASP  

Future possibilities:  
- **Startups** building APIs around `SAFE-T1001` defenses  
- **CISOs** adopting SAFE-MCP as MCP launch criteria  
- **LLM devs** embedding SAFE-MCP checks in dev workflows  

---

*Author’s Note: This blog is based on the SAFE-MCP Contributor Gathering (Sept 1, 2024). All details and cases are drawn from the live talks and discussions, aiming to faithfully capture the project’s vision and progress.*
