---
layout: post
title:  "Why AI-Driven Infrastructure Resilience Needs Search, Indexing, and Document Understanding"
date:   2026-05-09
categories: jekyll update
tags: 
  - AI Agent
  - AIOps
  - Indexing
  - Cloud
lang: en
---

{% include lang-switch.html %}

Modern cloud-native infrastructure has become too complex for traditional manual operations to handle reliably. A production incident is rarely caused by a single obvious failure. More often, it emerges from a combination of deployment changes, configuration drift, dependency failures, database latency, network routing issues, permission errors, resource bottlenecks, and historical operational risks.

Traditional monitoring systems can tell engineers where something is wrong, such as increased error rates, higher latency, pod restarts, or CPU spikes. However, they usually cannot quickly answer the more important questions:

- Why is it happening?
- What evidence supports this diagnosis?
- Is the current anomaly related to a recent deployment, configuration change, or dependency failure?
- Has a similar incident happened before?
- Which recovery action is safe?
- Does this action require human approval or escalation?

Therefore, an AI-driven infrastructure resilience system should not simply pass raw logs to a large language model and ask it to guess the root cause. A more reliable approach is to build an **evidence-grounded RCA Agent**. This agent first uses search, indexing, and document understanding to transform fragmented operational signals into searchable, connected, and reasoning-ready evidence. Only then should it perform root cause analysis, risk evaluation, and safe action recommendation.

In other words:

> AI-driven remediation is only as reliable as the operational evidence it can retrieve, understand, and connect.

---

# 1. System Overview: From Monitoring to an Evidence-Grounded RCA Agent

## 1.1 The Limitation of Traditional Monitoring

Traditional monitoring and observability systems usually operate around alerts, dashboards, and static thresholds. They are good at detecting symptoms such as:

- error rate increases;
- latency spikes;
- pod restarts;
- CPU or memory pressure;
- database connection growth;
- queue depth accumulation.

However, they usually only tell us:

> Something is wrong.

They do not automatically perform evidence-based reasoning, such as:

> Was this anomaly caused by a deployment ten minutes ago?  
> Is it limited to one region?  
> Is it related to a downstream dependency?  
> Has a similar incident happened before?  
> Does the runbook allow rollback?  
> Could this action cause a secondary failure?

This is the gap an AI-driven RCA Agent needs to address. Recent AIOps and agentic operations research has also moved from “letting the LLM read logs and guess the root cause” toward evidence-grounded RCA, where the model diagnoses incidents based on tool-retrieved evidence chains rather than acting as a factual memory store.[1][19]

---

## 1.2 Core Principle of an Evidence-Grounded RCA Agent

An RCA Agent should not directly read all logs and guess the answer. A safer approach is to build a workflow-first, evidence-grounded agent where the LLM acts as a planner, tool caller, and evidence synthesizer, with critic, checkpoint, and human-in-the-loop controls at key steps.[1][3][4]

```text
LLM plans
Tools retrieve
Ranker filters
LLM reasons from evidence
Policy verifies
Human approves high-risk actions
```

In this design, the LLM is not the data source and should not be the only decision-maker. It acts more like a:

- planner: deciding what evidence is needed;
- tool caller: invoking controlled tools to retrieve data;
- evidence synthesizer: summarizing retrieved evidence;
- reasoning assistant: generating candidate root causes and next-step recommendations.

A typical workflow can look like this:

```text
Alert / On-call / Chat Question
        ↓
Incident Context Builder
        ↓
Planner
        ↓
Retriever Router
        ↓
Evidence Pack Builder
        ↓
RCA Synthesizer
        ↓
Critic / Counterfactual Validator
        ↓
Root Cause Scoring
        ↓
Policy Governor
        ↓
Diagnosis + Safe Action Proposal
        ↓
Human Approval / Controlled Execution
        ↓
Post-check / Rollback / Incident Memory
```

In this architecture, the agent does not directly read all operational data. Instead, it uses controlled tools to access different evidence sources:

- log search;
- metrics query;
- trace query;
- deployment and configuration search;
- runbook retrieval;
- similar incident search;
- dependency graph query;
- policy verification.

A key design principle is: **do not start with a free-form conversational agent. Start with a workflow-first agent.**  
The system should explicitly separate Planner, Retriever, Synthesizer, Critic, and Governor steps. Each step should have clear inputs, outputs, checkpoints, and audit records.

---

# 2. Data Perception Layer: Building an Operational Evidence System

## 2.1 The Data Perception Layer Is Not Just Data Collection

The Data Perception Layer is sometimes misunderstood as simple data collection and cleaning. In an AI-driven resilience system, however, its role is much broader.

Its goal is to build an **operational evidence system** that can quickly answer:

- When did the incident start?
- Which service, region, cluster, or account is affected?
- Was there a deployment before the incident?
- Was there a configuration change or feature flag change?
- Which logs, metrics, and traces are related to the current symptom?
- Has a similar incident happened before?
- Is there a relevant runbook?
- Does the current action violate any safety constraint?
- Which dependency could be the upstream cause?

Therefore, the Data Perception Layer is not about storing all data. It is about organizing fragmented, heterogeneous, and constantly changing production signals into a searchable, connected, and reasoning-ready evidence network.

---

## 2.2 Understanding the Data Perception Layer Through the Lens of Search Systems

A large-scale search system does not merely crawl web pages. It usually includes:

- discover: finding data sources;
- select: selecting important data;
- schedule: deciding when to refresh data;
- fetch: collecting content;
- normalize: standardizing content;
- index: building indexes;
- rank: ranking results;
- serve: supporting retrieval and reasoning.

In infrastructure resilience, the data sources are not web pages. They are operational evidence:

- logs;
- metrics;
- traces;
- deployment events;
- code changes;
- configuration changes;
- security events;
- incident tickets;
- runbooks;
- service ownership metadata;
- dependency graphs;
- historical postmortems.

The mapping can be understood as:

| Search System Concept | RCA Agent Equivalent |
|---|---|
| Discover web pages | Discover log groups, metric streams, trace systems, CI/CD records, config repos, incident docs |
| Select important pages | Select relevant signals around affected service, region, time window, and error pattern |
| Schedule crawl | Schedule real-time ingestion, periodic refresh, and incident-time priority pull |
| Fetch content | Fetch logs, metrics, traces, configs, runbooks, and deployment records |
| Build index | Build searchable indexes over time, entity, keyword, semantic meaning, and dependency |
| Ranking | Rank evidence and candidate root causes |
| Serve intelligence | Provide evidence to the RCA Agent for diagnosis and safe action recommendation |

The Data Perception Layer can therefore be understood as:

> An operational search and evidence layer for production infrastructure.

This shift from passive data collection to active evidence service is consistent with recent agentic RCA and typed retrieval architectures.[1][6][19]

---

## 2.3 Canonical Incident Schema

The true bottleneck in RCA is not whether logs exist. It is whether different signals can be aligned. Logs, metrics, traces, Kubernetes events, deployment records, and configuration diffs must share a common schema.

A **Canonical Incident Schema** should include fields such as:

- `service.name`
- `service.namespace`
- `k8s.cluster.uid`
- `pod.name`
- `region`
- `environment`
- `owner`
- `deployment.revision`
- `change_id`
- `feature_flag`
- `trace_id`
- `incident_id`
- `time_bucket`
- `risk_level`
- `source_type`

With a shared schema, the system can connect evidence across different sources.

For example:

```text
metric spike:
  service.name = workspace-service
  region = us-east-1
  time_bucket = 10:05

log error:
  service.name = workspace-service
  pod.name = workspace-service-abc
  trace_id = xyz

deployment event:
  service.name = workspace-service
  deployment.revision = v2.3.1
  change_id = CHG-12345
  deployed_at = 10:01
```

This allows the agent to build a coherent incident context instead of treating these as isolated events. Observability standards such as OpenTelemetry also show that logs, metrics, traces, and resource attributes need shared semantic fields to support cross-signal correlation and downstream RCA.[5]

---

## 2.4 Change-Aware Preprocessing

Many production incidents are caused by recent changes:

- deployment;
- config diff;
- feature flag change;
- Helm values change;
- Kubernetes manifest change;
- IAM or permission change;
- routing rule change;
- database schema migration;
- dependency version upgrade.

The system should treat change events as first-class retrievable objects.

A structured change event may look like:

```json
{
  "change_id": "CHG-12345",
  "service": "workspace-service",
  "change_type": "config_change",
  "config_key": "db.connection.pool.max",
  "old_value": "20",
  "new_value": "100",
  "region": "us-east-1",
  "deployment_revision": "v2.3.1",
  "started_at": "10:01",
  "owner": "platform-team",
  "risk_level": "medium"
}
```

This enables the agent to answer:

> Which changes in the last 5-15 minutes are most relevant to the current incident?

This change-aware preprocessing is aligned with recent RCA research that emphasizes deployment-, configuration-, and context-aware diagnosis, because many production incidents are triggered by recent changes rather than sudden resource failures.[1][19]

---

## 2.5 Incident-Centric Incremental Memory

In addition to long-term indexes, the agent also needs short-term incident memory. A single incident may trigger multiple alerts and multiple on-call questions. Repeating the same retrieval process for each alert is expensive and may produce inconsistent conclusions.

An **Incident-Centric Incremental Memory** can store:

```text
Incident Window Memory
 ├── incident_id
 ├── time window
 ├── affected services
 ├── retrieved evidence
 ├── query plans
 ├── tool calls
 ├── candidate causes
 ├── rejected hypotheses
 ├── approved actions
 ├── post-check results
 └── final RCA summary
```

This helps:

- avoid repeated retrieval;
- preserve verified facts;
- record rejected hypotheses;
- reuse context across alerts;
- support postmortems and benchmark replay;
- create an auditable incident journal.

The memory should not store arbitrary model-generated text. It should store verified facts, cited evidence, rejected hypotheses, approved actions, and post-check results.

---

# 3. Index Layer Design: Different Data Requires Different Indexes

## 3.1 Why Indexing Is Foundational for an RCA Agent

Indexing is not the same as storage.

Storage means:

> We have the data.

Indexing means:

> We can find the most relevant evidence within seconds when an incident happens.

In an RCA scenario, the agent needs to quickly find evidence related to the current incident. For example, if the error rate of `workspace-service` starts increasing at 10:05, the system should quickly find:

- error logs around 10:05;
- the affected pod, region, and cluster;
- whether a deployment happened around 10:00;
- whether a specific config key was changed;
- whether traces show increased downstream database latency;
- whether a similar error pattern appeared in historical incidents;
- whether the runbook explains rollback conditions;
- whether the dependency graph shows upstream service degradation.

These tasks require different types of indexes. Recent hybrid retrieval and agentic RCA research also supports typed multi-index retrieval: different evidence types should use different indexes instead of being pushed into one vector database.[6][9][10]

---

## 3.2 Time Index

A time index retrieves relevant events around the incident window.

For example:

```text
incident_start_time = 10:05
query window = 09:45 - 10:20
```

The system can automatically retrieve:

- logs around the incident;
- metric trends;
- trace spans;
- deployment events;
- configuration changes;
- alert history.

It answers:

> What happened before and after the incident started?

A time index is especially useful for:

- logs;
- metrics;
- traces;
- deployment records;
- configuration changes;
- alert events.

### Tradeoff

| Option | Strength | Weakness |
|---|---|---|
| Wide time window | Higher recall | More noise and higher cost |
| Narrow time window | Lower cost and focused evidence | May miss gradual or earlier signals |
| Dynamic time window | Adapts to anomaly start time | Requires reliable start-time detection |

A practical approach is to start with an alert-based window and dynamically expand it based on anomaly detection, deployment history, and trace evidence.

---

## 3.3 Entity Index

An entity index connects evidence to specific system entities.

Common entities include:

- service;
- API;
- account;
- region;
- cluster;
- pod;
- database;
- endpoint;
- deployment version;
- config key;
- owner team.

For example, a log line may say:

```text
database connection timeout in workspace-service
```

The system needs to know that this log is related to:

- workspace-service;
- us-east-1;
- metadata-db;
- a specific pod;
- a recent deployment version;
- a related runbook;
- a service owner.

The entity index turns isolated logs into connected evidence.

---

## 3.4 Keyword / Inverted Index

A keyword index supports exact search over:

- error codes;
- exception names;
- config keys;
- API names;
- stack traces;
- request IDs;
- pod names;
- commit hashes.

Examples include:

- `AccessDeniedException`
- `NullPointerException`
- `HTTP 503`
- `connection refused`
- `OutOfMemoryError`
- `InvalidRequestException`

These should not rely only on embeddings. In production operations, exact identifiers are critical.

Therefore, systems like Elasticsearch or OpenSearch remain highly valuable. They are well suited for:

- log search;
- stack trace search;
- exact phrase search;
- time range filtering;
- service / region / cluster filtering;
- aggregation by error type.

---

## 3.5 Vector / Semantic Index

A vector index helps find information that is semantically similar but uses different wording.

For example:

| Current Issue | Historical Description |
|---|---|
| failed to assume role | IRSA credential exchange failed |
| S3 access denied | bucket policy rejected service account permission |
| driver pod stuck pending | insufficient node capacity for Spark driver |
| notebook cannot start kernel | kernel custom resource failed to launch |

These expressions are not identical, but they may describe the same type of failure. Embeddings can help the system find:

- similar incidents;
- related runbooks;
- semantically related postmortems;
- similar mitigation procedures;
- related error explanations.

However, semantic retrieval should not replace keyword search. A better design is hybrid retrieval because RCA requires exact token matching, metadata filtering, semantic recall, and reranking at the same time.[6]

```text
Exact keyword search
+ Metadata filter
+ Time window filter
+ Vector similarity
+ Graph context
+ Reranker
```

---

## 3.6 Graph / Relationship Index

A graph index represents system dependencies and impact paths.

For example:

```text
workspace-service
  → metadata-db
  → auth-service
  → S3
  → STS
  → Kubernetes API
```

It can represent relationships such as:

- service A calls service B;
- service B depends on database C;
- deployment D changed service A;
- config E affects component F;
- alert G belongs to cluster H;
- runbook I applies to error J.

A graph index is important for RCA because root cause analysis is not just about finding which component is red. It is about identifying:

> Which upstream change or dependency may have caused the downstream symptom?

GraphRAG, StateGraph, and Kubernetes RCA research also show that topology and runtime state graphs can improve multi-hop fault propagation analysis, although graph quality and freshness directly affect reliability.[7][8]

### Static Graph vs Dynamic StateGraph

A static dependency graph is useful but often incomplete or outdated. More advanced systems can maintain:

- **MetaGraph**: theoretical relationships between resource types;
- **StateGraph**: runtime state snapshots of resources;
- **Temporal Graph**: how states and dependencies change over time;
- **Incident Subgraph**: the relevant subset of the graph for the current incident.

For Kubernetes RCA, the agent can use the MetaGraph to determine which upstream and downstream resources to inspect, then query the StateGraph for runtime state changes during the incident window.

---

## 3.7 Structured Document Index

A structured document index is used for long-form operational knowledge such as runbooks, postmortems, SOPs, architecture documents, and security policies.

Instead of only splitting documents into chunks, it identifies the document structure:

```text
Runbook
 ├── Symptoms
 ├── Diagnosis
 │    ├── Check logs
 │    ├── Check metrics
 │    └── Check dependency health
 ├── Mitigation
 │    ├── Restart service
 │    ├── Rollback deployment
 │    └── Scale worker
 ├── Safety Constraints
 └── Escalation
```

When the agent asks:

> Is rollback safe?

The system can directly navigate to:

```text
Runbook → Mitigation → Rollback Procedure
Runbook → Safety Constraints → Rollback Conditions
```

This is more appropriate for safety-related questions than randomly retrieving top-k similar chunks.

---

## 3.8 Typed Hybrid Retrieval Router

Having multiple indexes is not enough. The system needs a **Typed Hybrid Retrieval Router**.

It first classifies query intent and then chooses the right indexes.

| Query Type | Main Indexes |
|---|---|
| Exact troubleshooting | keyword index + time/entity filter |
| Similar incident | vector index + incident memory |
| Runbook rule | structured document index |
| Change tracing | time index + deployment/config index |
| Dependency propagation | graph index + trace query |
| Safe execution | structured policy index + policy engine |

Example:

```text
Query: "Can we rollback workspace-service safely?"

Router:
  intent = safety / rollback
  indexes:
    - deployment/config index
    - structured runbook index
    - policy index
    - dependency graph
```

This router prevents the system from blindly querying everything and reduces latency, noise, and ambiguity. Recent hybrid search, composite retrieval, and agentic RCA practice also emphasize query routing and evidence fusion as key components of production-grade retrieval systems.[6][9][19]

---

## 3.9 Overall Tradeoff of Index Selection

| Index Type | Strength | Weakness | Best For |
|---|---|---|---|
| Time Index | Incident-window precision | Window selection may miss evidence | deployment/config/event correlation |
| Entity Index | Cross-source joining | Requires metadata quality | service/region/cluster alignment |
| Keyword Index | Exact and explainable | Weak semantic generalization | error codes, config keys, IDs |
| Dense Vector Index | Strong semantic recall | Weak exact-token handling | similar incidents, natural language docs |
| Sparse / Hybrid Vector | Balances semantics and token relevance | Requires tuning | RCA knowledge search |
| Graph Index | Multi-hop dependency reasoning | Costly to build and maintain | fault propagation |
| Structured Document Index | Precise section retrieval | Depends on document structure quality | runbooks, SOPs, policies |
| Incident Memory Index | Reuses incident context | Risk of memory pollution | multi-alert incident handling |

The key principle is:

> Do not put all evidence into one vector database. Use typed multi-index retrieval, query routing, and evidence fusion.

---

# 4. Document Understanding: Turning Operational Documents into Reasoning-Ready Knowledge

Document Understanding is not a standalone feature. It is a key part of the ingestion pipeline. It is mainly used for:

- runbooks;
- postmortems;
- incident tickets;
- deployment notes;
- architecture documents;
- policy documents;
- compliance documents;
- design documents.

It can be divided into four layers: structure understanding, semantic chunking, information extraction, and context linking.

---

## 4.1 Structure Understanding

Structure understanding identifies functional sections in a document, such as:

- symptom;
- diagnosis;
- mitigation;
- rollback;
- safety warning;
- escalation;
- root cause;
- timeline;
- follow-up action.

For example, a runbook may contain:

```text
Symptoms
Diagnosis Steps
Mitigation
Rollback Conditions
Safety Constraints
Escalation Policy
```

If the agent asks:

> Can we safely restart this service?

The system should not merely search for text containing “restart.” It should first navigate to:

```text
Runbook → Mitigation → Restart Procedure
Runbook → Safety Constraints → Restart Conditions
```

In automated remediation scenarios, safety rules are often more important than the action steps themselves.

---

## 4.2 Semantic Chunking

Traditional chunking may split text every 500 or 1,000 tokens. In operational systems, this can be risky because an action step or safety warning may be separated from its context.

Semantic chunking splits documents by complete meaning units, such as:

- a symptom chunk;
- a diagnosis procedure chunk;
- a mitigation procedure chunk;
- a rollback warning chunk;
- an escalation policy chunk.

For example, a Spark job failure runbook may be split into:

```text
Chunk 1: Symptom - Spark driver failed
Chunk 2: Diagnosis - Check pod event, service account, S3 access
Chunk 3: Mitigation - Refresh credentials or rollback config
Chunk 4: Safety Warning - Do not retry repeatedly before validating credentials
Chunk 5: Escalation - Contact platform team if STS errors persist
```

This allows the agent to retrieve complete, actionable, and context-aware knowledge units instead of fragmented text. Long-document retrieval and hierarchical RAG research also show that preserving document structure is often more reliable than simple fixed-size chunking for complex knowledge localization.[9][10]

---

## 4.3 Information Extraction

Information extraction converts unstructured or semi-structured text into structured fields.

From logs, the system may extract:

- service name;
- error type;
- endpoint;
- status code;
- latency;
- request ID;
- region;
- account ID;
- pod name.

From deployment notes, it may extract:

- changed service;
- version;
- commit ID;
- rollout region;
- changed config key;
- owner;
- rollback plan.

From postmortems, it may extract:

- symptom;
- impact;
- root cause;
- mitigation;
- prevention action;
- time to recovery.

From runbooks, it may extract:

- trigger condition;
- diagnostic command;
- safe action;
- unsafe action;
- rollback condition;
- escalation owner.

These extracted fields can be stored in:

- metadata databases;
- keyword search indexes;
- vector indexes;
- graph indexes;
- policy engines.

In practice, a hybrid extraction strategy is safer: deterministic parsers should handle timestamps, service names, regions, error codes, request IDs, and pod names, while LLM-based structured extraction can be used for symptoms, root causes, mitigations, and risk warnings, with validation before indexing.[1][5][20]

---

## 4.4 Context Linking

Context linking is the core of RCA.

For example:

```text
10:01 - workspace-service deployment started
10:04 - database latency increased
10:05 - API error rate increased
10:06 - logs show connection timeout
Historical incident - similar pattern caused by connection pool config
Runbook - check pool size before rollback
```

Each piece of evidence alone is insufficient. Together, they support a candidate root cause:

> A recent deployment may have introduced a database connection pool configuration issue.

This is the core capability of the Cross-Source Risk Intelligence Engine. It does not look at isolated alerts. It builds an evidence chain across logs, metrics, traces, deployments, configuration changes, historical incidents, and runbooks.

---

## 4.5 Evidence Pack

The agent should not directly consume raw search results. Instead, retrieval results should be packaged into a structured **Evidence Pack**.

Example:

```json
{
  "incident_context": {
    "service": "workspace-service",
    "region": "us-east-1",
    "start_time": "10:05",
    "symptom": "error rate increased"
  },
  "top_evidence": [
    {
      "type": "deployment",
      "time": "10:01",
      "summary": "workspace-service v2.3.1 deployed",
      "score": 0.92
    },
    {
      "type": "metric",
      "time": "10:04",
      "summary": "metadata-db latency increased",
      "score": 0.88
    },
    {
      "type": "log",
      "time": "10:06",
      "summary": "database connection timeout",
      "score": 0.86
    }
  ],
  "similar_incidents": [],
  "runbook_sections": [],
  "conflicting_evidence": [],
  "missing_evidence": []
}
```

The Evidence Pack controls input quality, reduces token cost, preserves source traceability, and supports audit and regression testing. It also helps reduce hallucination and reasoning drift by converting raw retrieval results into structured input with supporting evidence, conflicting evidence, missing evidence, source freshness, and confidence signals.[1][17][19]

---

# 5. Vectorless RAG: Retrieval Through Structural Navigation

## 5.1 What Is Vectorless RAG?

Traditional RAG usually relies on embeddings and a vector database. The workflow is roughly:

```text
Document
  ↓
Chunking
  ↓
Embeddings
  ↓
Vector Database
  ↓
Similarity Search
  ↓
Top-K Chunks
  ↓
LLM Output
```

The core idea is:

> Retrieve relevant text by semantic similarity.

Vectorless RAG follows a different approach. Instead of relying primarily on vector similarity, it navigates through document structure. The workflow is closer to:

```text
Document
  ↓
Structured Index
  ↓
Query Routing
  ↓
Hierarchical Navigation
  ↓
Precise Section Retrieval
  ↓
LLM Output
```

Its goal is not just to find similar text, but to find the right location. This is also the key idea behind Vectorless RAG discussions: for structured documents, retrieval should preserve hierarchy and logical position instead of relying only on embedding similarity.[9][10]

For example, for a runbook, the question is not:

> Which chunk is most similar to the word rollback?

The real question is:

> Where are the rollback safety conditions?  
> Where is the database migration warning?  
> Where is the escalation policy?

These questions are better served by structural navigation.

---

## 5.2 What Vectorless RAG Is Good For

Vectorless RAG is especially suitable for long and structured documents, such as:

- runbooks;
- SOPs;
- postmortems;
- architecture documents;
- compliance documents;
- security policies;
- deployment playbooks;
- operation manuals.

These documents usually have natural hierarchy:

```text
Document
 ├── Section
 │    ├── Subsection
 │    └── Table
 └── Appendix
```

When a question can be mapped to a document location, structural navigation can be more stable than similarity search.

For example:

> Can I restart this service safely?

A better retrieval path may be:

```text
Runbook
  → Mitigation
  → Restart Procedure
  → Safety Constraints
```

rather than retrieving chunks that merely contain the word “restart.”

---

## 5.3 What Vectorless RAG Cannot Replace

Vectorless RAG is useful, but it cannot replace the entire RCA system.

It cannot replace:

- log search;
- metrics query;
- distributed tracing;
- deployment and configuration metadata;
- service dependency graph;
- root cause scoring;
- policy verification.

The reason is that RCA systems deal not only with long documents, but also with large volumes of real-time, semi-structured, high-frequency data, such as:

- raw logs;
- metrics time series;
- trace spans;
- Kubernetes events;
- deployment events;
- configuration changes;
- high-cardinality operational metadata.

These data types are better handled by:

- Elasticsearch / OpenSearch;
- Prometheus / CloudWatch;
- Jaeger / Tempo;
- metadata databases;
- graph databases;
- stream processing.

Therefore, Vectorless RAG is best understood as a **structured knowledge navigation layer**, not a replacement for observability search. It is suitable for runbooks, SOPs, postmortems, architecture documents, and policy documents, but not for replacing log search, metrics query, trace query, or deployment metadata lookup.[6][9]

---

## 5.4 How Vectorless RAG Can Be Used in an RCA Agent

In an RCA Agent, Vectorless RAG can be used to retrieve structured operational knowledge.

For example:

```text
RCA Agent
 ├── Log Search Tool
 ├── Metrics Query Tool
 ├── Trace Query Tool
 ├── Deployment / Config Search Tool
 ├── Vectorless Structured Knowledge Retrieval Tool
 ├── Semantic Similar Incident Search Tool
 ├── Dependency Graph Tool
 └── Policy Verifier Tool
```

The Vectorless Structured Knowledge Retrieval Tool is mainly responsible for:

- runbook diagnosis sections;
- rollback safety sections;
- escalation policies;
- architecture dependency descriptions;
- compliance requirements;
- security operation policies.

It helps the agent find the correct section, not just similar text.

---

# 6. PageIndex-Style Retrieval: Hierarchical Document Indexing and Precise Section Retrieval

## 6.1 What Is PageIndex-Style Retrieval?

PageIndex-style retrieval is a document-structure-based retrieval approach. Representative implementations such as PageIndex build a table-of-contents-like hierarchy for long documents and then use reasoning-based navigation to locate relevant sections.[10][11]

Its core idea is:

> Build a hierarchical structure index similar to a table of contents, then navigate the tree based on the query to locate the most relevant section, subsection, or paragraph.

Compared with traditional vector RAG:

- traditional vector RAG relies on chunking, embeddings, and similarity search;
- PageIndex-style retrieval emphasizes document structure, hierarchical navigation, and precise section retrieval.

It is suitable for long documents, especially those with clear sections and where precise references are important.

For example:

```text
Runbook: Workspace Service Incident Response
 ├── Overview
 ├── Symptoms
 ├── Diagnosis
 │    ├── Check pod state
 │    ├── Check database latency
 │    └── Check S3 credential errors
 ├── Mitigation
 │    ├── Restart kernel
 │    ├── Rollback service
 │    └── Scale worker
 ├── Safety Constraints
 └── Escalation
```

For the question:

> Is rollback safe after database migration?

PageIndex-style retrieval can navigate to:

```text
Runbook
  → Mitigation
  → Rollback Service
  → Safety Constraints
  → Database Migration Warning
```

This is more suitable for safety decisions than simply returning a few similar chunks.

---

## 6.2 Offline Indexing Flow for PageIndex-Style Retrieval

PageIndex-style retrieval usually requires an offline or near-real-time indexing pipeline.

The flow can be:

```text
Runbooks / Postmortems / Architecture Docs
        ↓
Parse Document
        ↓
Detect Structure
        ↓
Build Tree:
  document → section → subsection → paragraph/table
        ↓
Attach Metadata:
  service, doc_type, owner, updated_at, risk_level
        ↓
Store Structured Index
```

Metadata is important. Examples include:

- service;
- system;
- doc_type;
- section_type;
- owner;
- updated_at;
- risk_level;
- environment;
- related incident;
- related dependency.

These metadata fields help the agent perform query routing and section filtering during incident-time retrieval.

---

## 6.3 Online Retrieval Flow for PageIndex-Style Retrieval

When an event is triggered or an on-call engineer asks a question, the agent can call a structured retrieval tool.

For example:

```text
Question:
"Is rollback safe for workspace-service after DB schema migration?"

        ↓

Query Router:
This is a safety / rollback question.

        ↓

Navigate:
Runbook
  → Workspace Service
  → Deployment Recovery
  → Rollback Conditions
  → Database Migration Safety

        ↓

Retrieve Precise Section

        ↓

Return evidence with section path
```

The final result can include:

- precise section content;
- document path;
- section path;
- last updated time;
- risk warning;
- applicable conditions.

For example:

```text
Retrieved Evidence:
Runbook → Workspace Service → Deployment Recovery → Rollback Conditions

Rule:
Rollback is only safe when the schema migration is backward compatible
and no active migration job is running.
```

This retrieval path is valuable for auditability. The system can explain:

> Why this rule was retrieved and where it came from.

---

## 6.4 How PageIndex-Style Retrieval Fits into an RCA Agent

PageIndex-style retrieval can serve as the **Structured Knowledge Retrieval** module in the RCA Agent.

The overall system can look like:

```text
Alert / Chat Question
        ↓
Incident Context Builder
        ↓
Query Router
        ↓
┌──────────────────────────────────────────────┐
│ 1. Log Search                                │
│    Elasticsearch / OpenSearch                │
│                                              │
│ 2. Metrics / Traces                          │
│    Prometheus / Jaeger / Tempo               │
│                                              │
│ 3. Deployment & Config Index                 │
│    Relational DB + keyword index             │
│                                              │
│ 4. Structured Knowledge Retrieval            │
│    PageIndex-style tree navigation           │
│                                              │
│ 5. Semantic Similarity Retrieval             │
│    Vector DB / embeddings                    │
│                                              │
│ 6. Dependency Graph                          │
│    Service catalog / graph DB                │
└──────────────────────────────────────────────┘
        ↓
Evidence Ranker
        ↓
Candidate Root Cause Scoring
        ↓
LLM Explanation + Recommended Action
        ↓
Policy Verifier + Human Approval
```

PageIndex-style retrieval mainly handles:

- runbooks;
- postmortems;
- architecture documents;
- operation manuals;
- security policies;
- compliance documents;
- deployment playbooks.

It does not handle raw logs, metrics, traces, or real-time event streams. In an RCA system, PageIndex-style retrieval should work as one structured knowledge retrieval module inside a broader hybrid retrieval layer that also includes keyword search, vector search, time-series retrieval, and graph queries.[6][10][11]

---

# 7. Hybrid RCA Retrieval: Not Vector vs. Vectorless, but Using the Right Method for Each Data Type

## 7.1 Why Hybrid Retrieval Is Necessary

In production RCA, different data types require different retrieval methods.

| Data Type | Best Retrieval Method |
|---|---|
| Raw logs / stack traces | Elasticsearch / OpenSearch keyword search |
| Metrics | Prometheus / CloudWatch time-series query |
| Traces | Jaeger / Tempo / APM trace query |
| Deployment / config records | Relational DB + metadata index |
| Historical incidents | Keyword search + vector semantic search |
| Runbooks / SOPs | Structured document navigation |
| Service dependencies | Graph index / service catalog |
| Safety policies | Structured retrieval + policy engine |

Therefore, the right architecture is not purely vector-based or purely vectorless. It is:

```text
Hybrid RCA Retrieval
= Observability Search
+ Keyword Search
+ Vector Semantic Search
+ Structured Knowledge Navigation
+ Dependency Graph
+ Evidence Ranking
```

Each data type should use the retrieval method that best fits its structure and purpose. For exact error troubleshooting, keyword search and metadata filters are more important; for historical experience transfer, vector search is useful; for runbook safety rules, structured document navigation is stronger; and for fault propagation, graph indexes are more appropriate.[6][7][10]

---

## 7.2 Query Routing: Different Questions Need Different Indexes

A key capability of the RCA Agent is query routing. Different questions should trigger different retrieval paths.

| Query Type | Retrieval Path |
|---|---|
| Why is the error rate increasing? | logs, metrics, traces, deployment index |
| Is rollback safe? | deployment history, runbook safety section, policy verifier |
| Has this happened before? | incident history, vector search, keyword search |
| Who owns this service? | service catalog, metadata DB |
| What does this error mean? | logs, runbook diagnosis, historical incidents |
| Is this action safe? | safety constraints, dependency graph, policy verifier |

A first version can use simple rules:

```text
if query contains "safe", "rollback", "restart":
    route to runbook safety sections + deployment index + policy checker

if query contains "similar", "happened before":
    route to incident history + vector search

if query contains "why", "root cause":
    route to logs + metrics + traces + deployment + dependency graph
```

Later, the LLM agent can generate a more dynamic search plan based on the query and incident context.

---

## 7.3 Late Fusion and Reranking

The hard part of hybrid retrieval is not querying multiple indexes. The hard part is fusing results from different indexes.

Evidence may come with:

- BM25 keyword score;
- dense vector similarity;
- sparse vector score;
- time proximity;
- entity match;
- graph distance;
- document section relevance.

These scores cannot be directly added without normalization.

A simple late fusion formula can be:

```text
normalized_score =
  w1 * keyword_score
+ w2 * semantic_score
+ w3 * metadata_match_score
+ w4 * time_proximity_score
+ w5 * graph_relevance_score
+ w6 * source_reliability_score
```

### Tradeoff

| Strategy | Strength | Weakness |
|---|---|---|
| Early fusion | Fast and simple | Hard to unify different modalities |
| Late fusion | Flexible and explainable | Requires score normalization |
| Learned reranker | Potentially stronger | Needs training data and online evaluation |
| Rule-based reranker | Controllable for MVP | Requires manual tuning |

For the MVP, rule-based late fusion is a practical starting point. A learned reranker can be added later after enough incident replay data is collected. This gradual approach is better suited for RCA because different indexes produce scores with different meanings, requiring normalization, source weighting, and reranking before the results can be safely used.[6]

---

# 8. RCA Workflow: From Event Trigger to Candidate Root Cause

## 8.1 Event Triggers

The RCA Agent can be triggered by:

- monitoring alerts;
- on-call engineer chat questions;
- incident tickets;
- deployment canary failures;
- SLO burn rate alerts;
- customer impact signals.

For example, an on-call engineer asks:

> Why is workspace-service error rate increasing in us-east-1?

The agent should not directly answer. It should first build the incident context:

- service = workspace-service;
- region = us-east-1;
- symptom = error rate increasing;
- time window = last 30 minutes;
- environment = production.

Then it generates a search plan.

---

## 8.2 Evidence Retrieval

The agent can call different tools:

```text
1. Log Search:
   Search error logs around incident window.

2. Metrics Query:
   Check error rate, latency, CPU, memory, DB connection count.

3. Trace Query:
   Identify slow downstream dependencies.

4. Deployment Index:
   Check recent deployments and config changes.

5. Structured Knowledge Retrieval:
   Retrieve runbook diagnosis and safety sections.

6. Semantic Similar Incident Search:
   Find similar historical incidents.

7. Dependency Graph:
   Find upstream and downstream services.

8. Time-Series Pattern Retrieval:
   Compare current metric pattern with historical abnormal windows.
```

The goal of this step is not to immediately produce a conclusion, but to collect enough evidence.

---

## 8.3 Time-Series Retrieval

Traditional RAG focuses on text, but many infrastructure incidents first appear in time-series metrics, such as:

- CPU utilization;
- memory pressure;
- disk I/O;
- network throughput;
- request latency;
- error rate;
- queue depth;
- DB connection count;
- pod restart count.

The RCA Agent should support **time-series retrieval**.

A practical workflow is:

1. extract metric patterns from the current incident window;
2. retrieve similar historical time-series patterns;
3. compare their associated root causes;
4. include them as candidate evidence.

Example:

```text
Current pattern:
  DB latency rises first
  API error rate rises 2 minutes later
  CPU remains normal

Historical similar pattern:
  Incident #123
  Root cause: connection pool saturation after config change
```

This allows the agent to reason not only from text, but also from metric dynamics.

### Tradeoff

| Method | Strength | Weakness |
|---|---|---|
| Threshold / change-point detection | Fast and explainable | Detects anomaly but not attribution |
| Similar time-series retrieval | Reuses historical incident patterns | Needs labeled historical incidents |
| TSFM / TS-RAG | Stronger for complex patterns | Higher engineering complexity |
| Rules + statistics + retrieval | Most practical for MVP | Requires tuning |

A practical MVP can start with:

> change-point detection + historical metric pattern search + Evidence Pack integration

without deploying a complex time-series foundation model initially. TS-RAG and RAG4CTS-style research shows that time-series data can also benefit from retrieval-augmented methods, but engineering adoption can begin with lightweight metric pattern retrieval.[12][13]

---

## 8.4 Evidence Synthesis

After retrieval, the system may find:

```text
10:01 - workspace-service deployment started
10:04 - metadata-db latency increased
10:05 - workspace-service error rate increased
10:06 - logs show database connection timeout
Historical incident - similar pattern caused by connection pool config
Runbook - check connection pool before rollback
```

The agent can synthesize this into an evidence chain:

> The error increase started shortly after deployment. The affected service depends on metadata-db. Metrics show database latency increased before the API error rate spike. Logs show connection timeout. A similar historical incident was caused by connection pool configuration. Therefore, a deployment-related DB connection configuration issue is a strong candidate root cause.

---

## 8.5 Critic and Counterfactual Validator

The RCA Agent should not only generate plausible root causes. It should actively look for counter-evidence.

A Critic / Counterfactual Validator checks:

- Is there conflicting evidence?
- Is there another more likely cause?
- Is this correlation or causation?
- If the assumption is reversed, does the conclusion still hold?
- If there had been no deployment, would the symptom still happen?
- If the database is the root cause, why are other database clients normal?

Example:

```text
Hypothesis:
  Recent deployment caused DB connection pool issue.

Counterfactual checks:
  1. Did the same error occur before deployment?
  2. Are services not touched by the deployment also affected?
  3. Did rollback or config revert improve metrics?
  4. Is the DB latency global or only visible from this service?
```

The Critic should output structured validation results:

```json
{
  "hypothesis": "Deployment introduced DB config issue",
  "supporting_evidence": ["deployment at 10:01", "DB timeout logs", "similar incident"],
  "conflicting_evidence": ["other DB clients are normal"],
  "missing_evidence": ["need config diff", "need trace sample"],
  "confidence_adjustment": "-0.10"
}
```

This reduces hallucination and reasoning drift. It is aligned with Reflexion, self-feedback, and counterfactual reasoning approaches: instead of only generating a plausible root cause, the system actively checks contradictory evidence, missing evidence, and whether the reasoning remains stable when assumptions are reversed.[3][14]

---

# 9. Ranking: Ranking Evidence and Candidate Root Causes

## 9.1 Evidence Ranking

The RCA Agent may retrieve too much evidence to send directly to the LLM. Evidence ranking is needed first.

A simple scoring function can be:

```text
evidence_score =
  0.25 * time_proximity_score
+ 0.20 * entity_match_score
+ 0.20 * text_relevance_score
+ 0.15 * semantic_similarity_score
+ 0.10 * source_reliability_score
+ 0.10 * severity_score
```

Each component has a clear meaning:

| Score | Meaning |
|---|---|
| time_proximity_score | How close the evidence is to the incident start time |
| entity_match_score | Whether service, region, cluster, or account matches |
| text_relevance_score | Keyword or BM25 relevance |
| semantic_similarity_score | Embedding similarity |
| source_reliability_score | Official runbook vs. informal chat |
| severity_score | Critical alert vs. low-level info log |

For example, a deployment that happened three minutes before the incident and affected the same service and region should rank high. A deployment from two weeks ago should rank much lower.

---

## 9.2 Enhanced Evidence Ranking

RCA-specific ranking can add more dimensions:

```text
evidence_score =
  base_retrieval_score
+ change_relevance_score
+ topology_relevance_score
+ freshness_score
+ contradiction_penalty
+ safety_priority_boost
```

Where:

- `change_relevance_score`: whether evidence is related to a recent change;
- `topology_relevance_score`: whether evidence lies on the dependency path;
- `freshness_score`: whether the index is fresh;
- `contradiction_penalty`: whether the evidence conflicts with other evidence;
- `safety_priority_boost`: whether the evidence is a safety constraint.

For example, if the user asks whether rollback is safe, a safety warning should be ranked highly even if its semantic similarity score is not the highest. In RCA, evidence ranking should consider not only text relevance but also time proximity, entity match, change relevance, topology relevance, freshness, source reliability, contradiction penalties, and safety priority.[6][7][17]

---

## 9.3 Root Cause Ranking

After evidence ranking, the system ranks candidate root causes.

A simple root cause scoring function can be:

```text
root_cause_score =
  0.30 * supporting_evidence_strength
+ 0.20 * temporal_causality
+ 0.20 * dependency_path_match
+ 0.15 * historical_similarity
+ 0.10 * blast_radius_match
+ 0.05 * absence_of_contradiction
```

For example:

### Candidate 1: Recent deployment introduced a DB config issue

Supporting evidence:

```text
deployment happened 3 minutes before incident
same service affected
DB connection timeout increased
historical incident had similar pattern
runbook recommends checking connection pool config
```

This candidate should receive a high score.

### Candidate 2: Database global outage

Supporting evidence:

```text
DB latency increased
```

Contradicting evidence:

```text
only one service affected
other DB clients normal
```

This candidate should receive a medium or low score.

### Candidate 3: Network outage

Supporting evidence:

```text
some timeout logs
```

Contradicting evidence:

```text
no other services in the same region affected
no network-level alerts
```

This candidate should receive a low score.

The first version does not need to be complex. It can start with rules and weights, then later introduce a learned reranker, causal graph, or anomaly detection model.

---

## 9.4 Output Should Include Counter-Evidence and Uncertainty

The RCA output should not only present the most likely root cause. It should also include counter-evidence and missing evidence.

Example:

```text
Most likely root cause:
  Recent deployment introduced DB connection pool configuration issue.

Supporting evidence:
  - Deployment happened 3 minutes before the incident.
  - DB timeout logs increased after deployment.
  - Similar historical incident had the same pattern.

Conflicting evidence:
  - Other services using the same DB are normal.

Missing evidence:
  - Need to inspect config diff.
  - Need trace sample from failed requests.

Confidence:
  Medium-high, pending config diff verification.
```

This is much more useful than a fluent but unsupported natural-language answer. Explicitly presenting supporting evidence, conflicting evidence, missing evidence, and confidence also makes the output easier to audit, replay, and evaluate against historical incidents.[1][17][19]

---

# 10. RCA Is Not a Single Model, but an Evidence-Grounded Pipeline

## 10.1 Avoid Starting with a Black-Box RCA Model

RCA should not be treated as a single model. A more feasible approach is to build RCA as a pipeline:

```text
Signal Detection
→ Evidence Retrieval
→ Correlation
→ Candidate Generation
→ Ranking
→ Explanation
→ Verification
→ Recommended Action
→ Post-check
```

A first version can use:

```text
Rule-based correlation
+ Hybrid retrieval
+ LLM reasoning
+ Policy verification
```

In other words, the system does not need to train a special “RCA large model” at the beginning. It can start by building an **evidence-grounded RCA pipeline**.

---

## 10.2 The Role of the LLM in the RCA Pipeline

The LLM can help with:

- generating a search plan;
- deciding which tools to call based on incident context;
- summarizing retrieved evidence;
- generating candidate root causes;
- explaining evidence chains;
- proposing next actions based on runbooks;
- producing human-readable incident summaries.

However, critical logic should not fully depend on the LLM. For example:

- timestamp parsing;
- service metadata join;
- region / cluster / account filtering;
- deployment lookup;
- permission checks;
- policy validation;
- high-risk action approval;
- command allowlist.

These are better handled by deterministic logic or a policy engine.

---

## 10.3 Detection and Localization as Replaceable Tools

The detection and localization layer does not need to rely on one algorithm. Different methods can be exposed as tools:

```text
Anomaly Detection Tool:
  Detect abnormal metrics and start time.

Change Correlation Tool:
  Identify recent deployments/config changes.

Graph RCA Tool:
  Rank root causes using dependency graph.

Graph-Free Fallback Tool:
  Rank candidates using correlation when graph is missing.

Time-Series Similarity Tool:
  Retrieve historical metric patterns.

Counterfactual Validator Tool:
  Test whether candidate cause still holds under alternative assumptions.
```

This allows the agent to orchestrate tools instead of trying to perform all statistical and causal reasoning internally. A tool-based RCA architecture is more practical for production systems because anomaly detection, causal graph scoring, graph-free fallback, and time-series similarity can be replaced or improved incrementally without training an end-to-end RCA model at the beginning.[15][21][22]

---

# 11. MVP Architecture: How to Build a Practical First Version

## 11.1 Practical Technology Stack

A realistic MVP can be designed as:

```text
Logs:
  Elasticsearch / OpenSearch

Metrics:
  Prometheus / CloudWatch

Traces:
  Jaeger / Tempo

Deployment / Config:
  PostgreSQL / MySQL / MariaDB

Runbooks / Incidents:
  Markdown / GitHub / Confluence
  + Structured Index
  + Vector Index
  + Keyword Index

Service Dependency:
  Service Catalog / Graph DB / Metadata Tables

Incident Memory:
  Append-only incident journal
  + short TTL evidence cache
  + searchable RCA summaries

Agent Orchestration:
  Python / FastAPI
  LangGraph / LlamaIndex / Custom Tool Framework

LLM:
  Query planning, structured extraction, RCA explanation

Embeddings:
  Semantic retrieval for similar incidents and runbooks

Policy:
  Rule engine, allowlist, action catalog, human approval for high-risk actions

AgentOps:
  Tool traces, evidence DAG, token/cost tracking, replayable checkpoints
```

The MVP goal can be:

> Build an AI-assisted RCA Agent that retrieves and ranks operational evidence from logs, metrics, deployments, runbooks, and incident history, then generates evidence-backed root cause candidates and safe next-step recommendations.

---

## 11.2 MVP Reference Architecture

```text
                 Alert / Chat Question
                         ↓
               Incident Context Builder
                         ↓
                   Query Router
                         ↓
        ┌────────────────┼─────────────────┐
        ↓                ↓                 ↓
   Log Search       Metrics Query      Trace Query
 Elasticsearch      Prometheus         Jaeger/Tempo
        ↓                ↓                 ↓
        └────────────────┼─────────────────┘
                         ↓
              Deployment / Config Index
                         ↓
          Structured Knowledge Retrieval
        PageIndex-style Tree Navigation
                         ↓
            Semantic Similar Incident Search
               Vector DB / Embeddings
                         ↓
              Service Dependency Graph
                         ↓
              Incident Window Memory
                         ↓
                 Evidence Pack
                         ↓
                 Evidence Ranker
                         ↓
          Candidate Root Cause Generator
                         ↓
          Critic / Counterfactual Validator
                         ↓
              Root Cause Scoring
                         ↓
        Diagnosis + Safe Action Proposal
                         ↓
        Policy Verifier + Human Approval
                         ↓
           Controlled Execution / Post-check
                         ↓
        Incident Memory / Audit / Replay
```

---

## 11.3 Performance and Scalability Design

The bottleneck of an RCA system is often not the LLM. In a multi-index RCA system, the bottlenecks are usually:

- index write throughput;
- log time range scan;
- vector memory;
- trace search;
- graph traversal;
- cross-modal fan-out;
- stale cache;
- score fusion latency.

A practical design is:

```text
Hot / Warm / Cold Storage
+ Summary Index
+ Incident Evidence Cache
+ Modality-specific Scaling
```

### Hot / Warm / Cold Design

| Layer | Content | Goal |
|---|---|---|
| Hot | Recent 1-7 days full logs/traces/vectors | Low-latency RCA |
| Warm | Recent 1-4 weeks compressed data | Incident replay / trend analysis |
| Cold | Long-term RCA summaries / rollups | Low-cost historical learning |
| Summary Index | incident summary, root cause, mitigation, embedding | Fast similar incident retrieval |

### Evidence Cache

For the same incident window, the system can cache:

- query plan;
- service graph;
- top evidence;
- candidate causes;
- runbook sections;
- policy decisions.

This reduces repeated fan-out across multiple alerts.

---

## 11.4 Index Freshness and Consistency

One major risk in a multi-index system is freshness inconsistency.

For example:

- logs may already be in OpenSearch;
- deployment events may not yet be in the database;
- vector index may not be refreshed;
- service graph may still reflect an old topology;
- a runbook may have been updated but not re-indexed.

This can lead to incorrect diagnosis.

Mitigation strategies:

1. every evidence item should include `indexed_at` and `source_updated_at`;
2. the Evidence Pack should expose freshness metadata;
3. high-risk actions should query real-time APIs before execution;
4. use append-only event streams where possible;
5. use versioned document IDs;
6. record evidence versions in the final RCA.

Example output:

```text
Freshness warning:
  Deployment index is fresh within 30 seconds.
  Runbook index was last updated 2 days ago.
  Service graph snapshot is 15 minutes old.
```

Freshness should be treated as a first-class reliability signal. Recent discussions on agentic operations and hybrid retrieval also emphasize that multi-index systems must expose freshness, index version, and evidence provenance; otherwise, an agent may reason from stale evidence.[6][9][17]

---

# 12. Core Design Principles

## 12.1 Do Not Let the LLM Guess from Raw Logs

A safer workflow is:

```text
LLM plans
Tools retrieve
Ranker filters
LLM reasons from evidence
Critic challenges
Policy verifies
Human approves high-risk actions
```

---

## 12.2 Do Not Use Only a Vector Database

Operational RCA requires hybrid retrieval:

```text
Exact search
+ Semantic search
+ Metadata filter
+ Time correlation
+ Dependency graph
+ Structured document navigation
+ Evidence reranking
```

---

## 12.3 Vectorless RAG and PageIndex-Style Retrieval Are Structured Knowledge Retrieval Layers, Not the Entire RCA System

They are useful for:

- runbooks;
- postmortems;
- SOPs;
- architecture documents;
- policy documents.

They should not replace:

- logs;
- metrics;
- traces;
- deployment metadata;
- service dependency graphs;
- policy verification.

---

## 12.4 RCA Should Not Start as a Black-Box Model

A more feasible first version is:

```text
Evidence-grounded RCA pipeline
```

Later, the system can add:

- anomaly detection;
- causal graph;
- learned reranker;
- incident similarity model;
- time-series retrieval;
- automated remediation verifier.

---

## 12.5 Execution Must Be Separated from LLM Reasoning

The agent can recommend actions, but it should not freely generate shell commands or arbitrary API calls. Production execution should go through:

- Action Catalog;
- parameterized runbook;
- policy engine;
- approval workflow;
- pre-check;
- post-check;
- rollback path.

Example:

```text
Action:
  rollback_service

Parameters:
  service = workspace-service
  target_revision = v2.3.0
  region = us-east-1

Preconditions:
  no active database migration
  error rate above threshold
  rollback revision exists
  approval required if blast radius > one region

Post-check:
  error rate decreases within 5 minutes
  latency returns to baseline
  no new critical alert

Rollback/freeze:
  stop further rollout if post-check fails
```

This prevents the agent from turning diagnostic suggestions into unsafe operations. SafeAgent, policy-controlled tool use, and action governance research also emphasize that production execution should go through parameterized actions, policy gates, pre-checks, post-checks, and human approval.[2][16]

---

## 12.6 Explainability Means Evidence DAG, Not Just a Summary

In production RCA, explainability should not be just a natural-language summary. It should be a reviewable evidence graph.

An Evidence DAG can include:

- query;
- tool call;
- result item;
- candidate cause;
- supporting evidence;
- conflicting evidence;
- policy decision;
- action result;
- post-check outcome.

Example:

```text
Alert
  → Query logs
  → Error timeout evidence
  → Query deployment
  → Recent config change
  → Query graph
  → metadata-db dependency
  → Candidate cause
  → Critic challenge
  → Policy decision
  → Recommended action
```

This allows post-incident review to answer:

- what the agent searched;
- why it searched;
- which evidence supported the conclusion;
- which evidence contradicted the conclusion;
- why an action was allowed or blocked.

This Evidence DAG design is also aligned with AgentOps and LLM observability practices, where production agents need tool traces, retrieval traces, policy decisions, and action outcomes rather than only natural-language explanations.[4][17]

---

# 13. Evaluation: How to Verify the System

An RCA Agent should not be evaluated only by whether its answer sounds fluent. Evaluation should cover retrieval, RCA accuracy, safety, latency, and auditability. Benchmarks such as AIOpsLab, Cloud-OpsBench, and RCAEval also show that agentic operations should be evaluated across tool use, environment interaction, execution safety, and replayability, not just final-answer accuracy.[15][18]

## 13.1 Retrieval Metrics

- Evidence Recall@5;
- MRR / nDCG;
- exact token retrieval accuracy;
- runbook section accuracy;
- similar incident retrieval accuracy;
- index freshness lag;
- p50 / p95 retrieval latency.

## 13.2 RCA Metrics

- AC@1;
- AC@3;
- top-k root cause coverage;
- time-to-first-useful-hypothesis;
- missing-modality robustness;
- graph corruption robustness.

## 13.3 Safety Metrics

- unsafe action suggestion rate;
- policy violation rate;
- manual override rate;
- rollback success rate;
- post-check pass rate;
- blast radius containment.

## 13.4 AgentOps Metrics

- tool call count;
- token cost;
- failed tool call rate;
- hallucinated evidence rate;
- citation precision;
- audit reconstruction time;
- critic correction rate.

## 13.5 Ablation Tests

A useful evaluation plan is progressive ablation:

```text
Baseline:
  logs + metrics only

Add traces:
  logs + metrics + traces

Add changes:
  logs + metrics + traces + deployment/config

Add graph:
  add dependency graph

Add semantic retrieval:
  add vector incident search

Add structured docs:
  add runbook PageIndex-style retrieval

Add critic:
  add counterfactual validator
```

The goal is to measure how each layer improves RCA accuracy, latency, and safety. This is especially important for a layered RCA architecture because ablation can show whether traces, deployment/config indexes, graph indexes, vector incident search, structured runbook retrieval, and the critic each provide measurable value.[15][18]

---

# 14. Conclusion

The key to AI-driven remediation is not only model intelligence. It is the quality of the evidence foundation. A reliable autonomous resilience system must first solve how to discover, index, understand, connect, and rank operational evidence.

For a production-grade RCA Agent, the best approach is neither pure vector RAG nor pure vectorless retrieval. It is a hybrid architecture:

```text
Hybrid RCA Agent
= Observability Search
+ Metadata Indexing
+ Semantic Retrieval
+ Structured Knowledge Navigation
+ Dependency Graph
+ Time-Series Pattern Retrieval
+ Evidence Ranking
+ Critic Validation
+ Policy-Governed Remediation
```

This architecture allows infrastructure operations to move from passive alerting to evidence-based diagnosis, and eventually toward safe, verifiable, and auditable automated remediation.

The real system ceiling is not determined by simply using a larger model. It is determined by whether the evidence layer is:

- typed;
- multimodal;
- time-aware;
- change-aware;
- explainable;
- auditable;
- replayable;
- verifiable.

That is the practical path toward production-grade AI agents for cloud-native infrastructure diagnosis and resilience.

---

# References
[1] AIOps Solutions for Incident Management: Technical Guidelines and A Comprehensive Literature Review.  
[2] AWS Systems Manager Automation, Open Policy Agent, and policy-as-code / approval-based automation practices for controlled remediation.  
[3] ReAct / Reflexion / workflow-based agent reasoning.  
[4] LangGraph workflow, checkpointing, and human-in-the-loop design.  
[5] OpenTelemetry semantic conventions and Collector architecture.  
[6] OpenSearch / Elastic hybrid search, sparse retrieval, filtering, and reranking pipeline.  
[7] GraphRAG and graph-augmented retrieval for multi-hop reasoning.  
[8] StateGraph / MetaGraph approaches for Kubernetes RCA.  
[9] Hierarchical long-document retrieval and structured document indexing.  
[10] Vectorless RAG and PageIndex-style structured retrieval.  
[11] VectifyAI PageIndex.  
[12] TS-RAG: Retrieval-Augmented Generation based Time Series Foundation Models.  
[13] RAG4CTS / retrieval-augmented generation with covariate time series.  
[14] Counterfactual reasoning and causal validation for LLM agents.  
[15] RCAEval / AIOpsLab / Cloud-OpsBench style RCA evaluation.  
[16] SafeAgent / policy-controlled tool use / action governance.  
[17] AgentOps / LLM observability / tool trace and evidence auditability.  
[18] Cloud-native AI operations benchmark and remediation evaluation.
[19] Recent tool-augmented and agentic RCA work, including AMER-RCL / TAMO-style RCA agents and related tool-use RCA research.  
[20] Online and adaptive log parsing methods such as HELP-style online log template extraction for evolving production logs.  
[21] PyRCA and industrial RCA algorithm frameworks for unified anomaly detection and causal RCA pipelines.  
[22] BARO, DynaCausal, OCEAN, and related work on change-point detection, dynamic causal learning, and graph-free / graph-based RCA.  
