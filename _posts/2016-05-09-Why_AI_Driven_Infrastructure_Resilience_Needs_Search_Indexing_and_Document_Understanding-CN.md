---
layout: post
title:  "为什么 AI 驱动的基础设施韧性需要搜索、索引与文档理解"
date:   2016-05-09
categories: jekyll update
tags: 
  - AI Agent
  - AIOps
  - Indexing
  - Cloud
lang: zh
---

{% include lang-switch.html %}

现代云原生基础设施的复杂性已经远远超过了传统人工运维可以稳定处理的范围。一次生产事故往往不是由单一故障引起，而是由部署变更、配置漂移、依赖服务异常、数据库延迟、网络路由问题、权限错误、资源瓶颈和历史遗留风险共同触发。

传统监控系统可以告诉工程师“哪里出问题了”，例如 error rate 上升、latency 增加、pod restart 或 CPU spike。但它们通常无法快速回答更关键的问题：

- 为什么出问题？
- 哪些证据支持这个判断？
- 当前异常和最近的 deployment、configuration change、dependency failure 是否有关？
- 历史上是否发生过类似问题？
- 哪个恢复动作是安全的？
- 是否需要人工审批或升级处理？

因此，AI 驱动的基础设施韧性系统不能只是简单地把日志交给大语言模型，让模型直接猜测根因。更可靠的方式是构建一个 **evidence-grounded RCA Agent**：先通过搜索、索引和文档理解，把分散的系统信号转化为可检索、可关联、可推理的证据基础，然后让 Agent 基于证据进行根因分析、风险判断和恢复建议。

换句话说：

> AI 自动恢复是否可靠，取决于它能否找到、理解并关联正确的运维证据。

---

# 1. 系统总体思路：从 Monitoring 到 Evidence-Grounded RCA Agent

## 1.1 传统监控的局限

传统 monitoring / observability 系统通常围绕 alerts、dashboards 和 static thresholds 工作。它们擅长检测异常，例如：

- error rate 超过阈值；
- latency 突然升高；
- pod restart 增加；
- CPU / memory 使用率异常；
- database connection 增加；
- queue depth 堆积。

但是，传统系统通常只能告诉我们：

> Something is wrong.

它不能自动完成完整的证据推理，例如：

> 这个异常是否由 10 分钟前的 deployment 引起？  
> 是否只影响某个 region？  
> 是否和某个 downstream dependency 有关？  
> 历史上是否有相似 incident？  
> runbook 里是否允许 rollback？  
> 这个 action 是否可能造成 secondary failure？

这就是 AI-driven RCA Agent 需要解决的问题。

---

## 1.2 Evidence-Grounded RCA Agent 的核心原则

RCA Agent 不应该直接“看全部日志然后猜答案”。更合理的方式是：

```text
LLM plans
Tools retrieve
Ranker filters
LLM reasons from evidence
Policy verifies
Human approves high-risk actions
```

也就是说，LLM 不是数据源，也不是唯一判断者。LLM 更像是：

- planner：决定需要查哪些证据；
- tool caller：调用受控工具检索数据；
- evidence synthesizer：基于检索结果总结证据链；
- reasoning assistant：生成候选根因和下一步建议。

一个典型 workflow 可以是：

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

在这个架构中，Agent 不是直接读取所有数据，而是通过受控工具访问不同证据源：

- log search；
- metrics query；
- trace query；
- deployment / config search；
- runbook retrieval；
- similar incident search；
- dependency graph query；
- policy verification。

一个重要原则是：**不要把 RCA 做成自由对话式 Agent，而应该先做 workflow-first 的 Agent。**  
也就是说，先把 Planner、Retriever、Synthesizer、Critic、Governor 这些步骤显式拆开，每一步都有明确输入、输出和审计记录。等系统稳定后，再在确实需要角色分工的地方引入多 Agent。

---

# 2. Data Perception Layer：建立 Operational Evidence System

## 2.1 Data Perception Layer 不是简单的数据收集

很多人会把 Data Perception Layer 理解为“收集和清洗数据”。但在 AI-driven resilience 系统中，它的作用远不止如此。

它的目标是建立一个 **operational evidence system**，让系统可以在事故发生时快速回答：

- 事故什么时候开始？
- 哪个 service、region、cluster、account 受影响？
- 事故发生前是否有 deployment？
- 是否有 configuration change 或 feature flag change？
- 哪些 logs、metrics、traces 和当前症状相关？
- 历史上是否发生过类似 incident？
- 是否存在相关 runbook？
- 当前 action 是否违反 safety constraint？
- 哪些依赖服务可能是上游根因？

所以 Data Perception Layer 的核心不是“把所有数据存起来”，而是把分散、异构、动态变化的生产系统信号组织成一个可搜索、可关联、可推理的证据网络。

---

## 2.2 从 Search System 的角度理解 Data Perception Layer

大规模搜索系统不是简单抓取网页。它通常包含：

- discover：发现数据源；
- select：选择重要数据；
- schedule：决定什么时候更新；
- fetch：抓取内容；
- normalize：标准化；
- index：建立索引；
- rank：排序；
- serve：支持检索和推理。

在基础设施韧性系统中，数据源不再是网页，而是生产系统里的 operational evidence：

- logs；
- metrics；
- traces；
- deployment events；
- code changes；
- configuration changes；
- security events；
- incident tickets；
- runbooks；
- service ownership metadata；
- dependency graphs；
- historical postmortems。

对应关系可以这样理解：

| Search System 概念 | RCA Agent 中的对应实现 |
|---|---|
| Discover web pages | Discover log groups, metric streams, trace systems, CI/CD records, config repos, incident docs |
| Select important pages | Select relevant signals around affected service, region, time window, error pattern |
| Schedule crawl | Schedule real-time ingestion, periodic refresh, incident-time priority pull |
| Fetch content | Fetch logs, metrics, traces, configs, runbooks, deployment records |
| Build index | Build searchable indexes over time, entity, keyword, semantic meaning, dependency |
| Ranking | Rank evidence and candidate root causes |
| Serve intelligence | Provide evidence to RCA Agent for diagnosis and safe action recommendation |

因此，Data Perception Layer 可以理解为：

> An operational search and evidence layer for production infrastructure.

---

## 2.3 Canonical Incident Schema：统一证据语义

真正决定 RCA 上限的，不是“有没有日志”，而是不同观测信号能不能被统一对齐。Logs、metrics、traces、Kubernetes events、deployment records、configuration diffs 如果没有统一 schema，就很难在 incident-time 被可靠关联。

因此，Data Perception Layer 需要一个 **Canonical Incident Schema**。至少应包含：

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

这样做的价值是：不同数据源可以被映射到同一实体命名空间中。

例如：

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

统一 schema 后，Agent 才能把这些信号连成同一个 incident context，而不是把它们当作孤立事件。

---

## 2.4 Change-Aware Preprocessing：把变更变成一等证据

很多生产事故不是资源突然坏了，而是由最近的 change 引发：

- deployment；
- config diff；
- feature flag change；
- Helm values change；
- Kubernetes manifest change；
- IAM / permission change；
- routing rule change；
- database schema migration；
- dependency version upgrade。

因此，系统不能只采集 logs、metrics、traces，还必须把 **change events** 结构化，并作为可检索对象。

一个 change event 可以包含：

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

这种结构化 change index 可以帮助 Agent 快速回答：

> 事故发生前 5-15 分钟内，哪些变更最可能相关？

---

## 2.5 Incident-Centric Incremental Memory：围绕事故窗口建立短期记忆

除了长期索引，RCA Agent 还需要短期记忆。因为一个 incident 可能触发多个 alerts，多个 on-call 查询也可能重复追问同一个问题。如果每次都重新查 logs、metrics、deployment、runbooks，成本高、延迟高，也容易出现不一致结论。

可以建立 **Incident-Centric Incremental Memory**：

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

它的作用是：

- 避免同一事故窗口内重复检索；
- 记录被验证过的事实；
- 记录被否定的假设；
- 支持后续告警复用上下文；
- 支持 postmortem 和 benchmark replay；
- 形成可审计 incident journal。

注意：短期记忆不能随意写入模型生成内容。更稳妥的做法是只写入：

- 通过工具验证的事实；
- 明确来源的证据；
- 被 Critic 验证过的候选根因；
- 被否定的假设；
- 已执行动作和 post-check 结果。

---

# 3. 索引层设计：不同数据使用不同索引

## 3.1 为什么索引是 RCA Agent 的基础

索引不是简单存储。

存储是：

> 我有这些数据。

索引是：

> 当事故发生时，我能在几秒内找到最相关的证据。

在 RCA 场景中，Agent 需要从大量数据中快速找到和当前 incident 有关的证据。比如 `workspace-service` 的 error rate 在 10:05 开始上升，系统需要快速找到：

- 10:05 前后有哪些 error logs？
- 哪个 pod、region、cluster 出现异常？
- 是否在 10:00 附近有 deployment？
- 是否修改了某个 config key？
- traces 是否显示 downstream database latency 升高？
- 历史 incident 中是否出现过类似 error pattern？
- runbook 是否说明了 rollback 条件？
- dependency graph 是否显示上游服务异常？

这些都依赖不同类型的索引。

---

## 3.2 Time Index：时间索引

Time index 用于根据事故时间窗口定位相关事件。

例如：

```text
incident_start_time = 10:05
query window = 09:45 - 10:20
```

系统可以自动拉取：

- 事故前后的 logs；
- metrics trend；
- trace spans；
- deployment events；
- config changes；
- alert history。

它回答的问题是：

> 事故发生前后发生了什么？

Time index 特别适合：

- logs；
- metrics；
- traces；
- deployment records；
- configuration changes；
- alert events。

### Tradeoff

| 方案 | 优点 | 缺点 |
|---|---|---|
| 宽时间窗口 | Recall 高，不容易漏掉早期信号 | 噪声大，检索成本高 |
| 窄时间窗口 | 成本低，证据更集中 | 可能漏掉较早的 deployment 或渐进式异常 |
| 动态窗口 | 可根据异常起点自动调整 | 实现复杂，需要可靠的 anomaly start detection |

一个实用做法是：先用 anomaly detection 或 alert timestamp 找初始窗口，再根据 deployment、metric trend 和 trace path 动态扩展窗口。

---

## 3.3 Entity Index：实体索引

Entity index 用于把证据绑定到具体系统实体。

常见实体包括：

- service；
- API；
- account；
- region；
- cluster；
- pod；
- database；
- endpoint；
- deployment version；
- config key；
- owner team。

例如，一条 log 里出现：

```text
database connection timeout in workspace-service
```

系统需要知道它关联到：

- workspace-service；
- us-east-1；
- metadata-db；
- specific pod；
- recent deployment version；
- related runbook；
- service owner。

Entity index 的作用是把孤立日志变成可关联证据。

### Tradeoff

Entity index 的难点在于命名一致性。例如同一个服务可能在不同系统里叫：

- `workspace-service`
- `workspace_svc`
- `ws-service`
- `mdas-workspace`

如果没有统一命名和 alias mapping，Agent 可能会漏掉关键证据。因此，entity index 需要配合：

- canonical service registry；
- alias table；
- ownership metadata；
- deployment metadata；
- resource enrichment。

---

## 3.4 Keyword / Inverted Index：关键词与倒排索引

Keyword index 用于精确查找：

- error code；
- exception name；
- config key；
- API name；
- stack trace；
- request ID；
- pod name；
- commit hash。

例如：

- `AccessDeniedException`
- `NullPointerException`
- `HTTP 503`
- `connection refused`
- `OutOfMemoryError`
- `InvalidRequestException`

这些内容不能只依赖 embedding。因为在生产运维场景里，精确标识符非常重要。

因此，Elasticsearch / OpenSearch 这类系统仍然非常有价值。它们适合处理：

- log search；
- stack trace search；
- exact phrase search；
- time range filter；
- service / region / cluster filter；
- aggregation by error type。

### Tradeoff

| 方案 | 优点 | 缺点 |
|---|---|---|
| 纯 keyword search | 精确、可解释、速度快 | 对同义表达和历史经验迁移弱 |
| BM25 + metadata filter | 适合日志、错误码、配置项 | 需要高质量字段抽取 |
| Keyword + aggregation | 可发现 top errors / top pods | 对跨模态因果关系理解有限 |

Keyword search 很适合作为 RCA 的第一层召回，尤其用于 exact token 压力测试，例如 error code、pod UID、commit SHA、feature flag key。

---

## 3.5 Vector / Semantic Index：语义索引

Vector index 用于查找“意思相近但字面不同”的内容。

例如：

| 当前问题 | 历史记录里的表达 |
|---|---|
| failed to assume role | IRSA credential exchange failed |
| S3 access denied | bucket policy rejected service account permission |
| driver pod stuck pending | insufficient node capacity for Spark driver |
| notebook cannot start kernel | kernel custom resource failed to launch |

这些表达不完全相同，但语义上可能指向同类问题。Embedding 可以帮助系统找到：

- similar incidents；
- related runbooks；
- semantically related postmortems；
- similar mitigation procedures；
- related error explanations。

但是，semantic retrieval 不应该替代 keyword search。更合理的是 hybrid retrieval：

```text
Exact keyword search
+ Metadata filter
+ Time window filter
+ Vector similarity
+ Graph context
+ Reranker
```

### Dense vs Sparse vs Hybrid

Vector search 还可以进一步拆分：

| 类型 | 适合场景 | 优点 | 缺点 |
|---|---|---|---|
| Dense vector | 相似 incident、自然语言 runbook、postmortem | 语义泛化强 | 对精确标识符弱 |
| Sparse vector / learned sparse retrieval | 兼顾 token-level 可解释性和语义扩展 | 可解释性比 dense 好，可走倒排结构 | 需要模型和索引配合 |
| Hybrid dense + sparse + BM25 | RCA 场景最稳 | 精确匹配和语义召回兼顾 | 需要 score normalization 和 reranking |

对于 RCA 系统，推荐使用 hybrid，而不是 vector-only。

---

## 3.6 Graph / Relationship Index：关系索引

Graph index 用于表示系统依赖关系和影响路径。

例如：

```text
workspace-service
  → metadata-db
  → auth-service
  → S3
  → STS
  → Kubernetes API
```

它可以表示：

- service A calls service B；
- service B depends on database C；
- deployment D changed service A；
- config E affects component F；
- alert G belongs to cluster H；
- runbook I applies to error J。

Graph index 对 RCA 很重要，因为根因分析不是只看“哪里红了”，而是看：

> 哪个上游变化可能导致了下游异常？

### Static Graph vs Dynamic StateGraph

传统 service dependency graph 往往是静态的，但真实系统的依赖关系会随时间变化。因此，可以进一步引入：

- **MetaGraph**：定义理论上的资源类型关系，例如 Deployment → ReplicaSet → Pod → PVC；
- **StateGraph**：记录某一时间窗口内资源的实际状态，例如 Pod 状态、PVC 是否 Bound、Node 是否 Ready；
- **Temporal Graph**：记录依赖和状态随时间的变化；
- **Incident Subgraph**：只截取和当前 incident 相关的一小部分图。

例如 Kubernetes 场景中，Agent 可以先用 MetaGraph 判断应该查哪些上下游资源，再从 StateGraph 里拉取这些资源在 incident window 内的状态变化。

### Tradeoff

| 方案 | 优点 | 缺点 |
|---|---|---|
| 静态依赖图 | 简单、成本低 | 容易过期，无法表达运行时状态 |
| Trace-derived service graph | 更贴近真实调用路径 | 依赖 trace 覆盖率 |
| Dynamic StateGraph | 对 K8s / cloud-native RCA 很强 | 实现复杂，数据量大 |
| Graph-free fallback | 图缺失时仍可工作 | 因果路径解释能力弱 |

建议做法是：**Graph-first, graph-optional**。有可信 graph 时优先使用拓扑推理；graph 缺失或不可信时，自动回退到 correlation-first / graph-free RCA。

---

## 3.7 Structured Document Index：结构化文档索引

Structured document index 用于处理 runbooks、postmortems、SOPs、architecture docs、security policies 等长文档。

它不是只把文档切成 chunks，而是识别文档结构：

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

这样当 Agent 问：

> Is rollback safe?

系统可以直接导航到：

```text
Runbook → Mitigation → Rollback Procedure
Runbook → Safety Constraints → Rollback Conditions
```

这比随机找 top-k similar chunks 更适合安全相关问题。

---

## 3.8 Typed Hybrid Retrieval Router：让不同问题走不同索引

仅仅拥有多个索引还不够。系统还需要一个 **Typed Hybrid Retrieval Router**。

它的职责是先判断 query intent，再决定调用哪些索引。

可以把 on-call query 分成几类：

| Query 类型 | 主要索引 |
|---|---|
| 精确排障 | keyword index + time/entity filter |
| 相似事故 | vector index + incident memory |
| runbook 规则 | structured document index |
| 变更追溯 | time index + deployment/config index |
| 依赖传播 | graph index + trace query |
| 安全执行 | structured policy index + policy engine |

例如：

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

再例如：

```text
Query: "Have we seen this AccessDeniedException before?"

Router:
  intent = similar incident + exact error
  indexes:
    - keyword index
    - vector incident index
    - incident memory
```

这个 router 是 Hybrid RCA Retrieval 的关键。没有 router，多索引系统很容易退化成“什么都查一点”，导致延迟高、噪声大、结果难以解释。

---

## 3.9 索引选择的总体 Tradeoff

| 索引类型 | 优点 | 缺点 | 最适合场景 |
|---|---|---|---|
| Time Index | 精准限定 incident window | 时间窗选择错误会漏证据 | deployment/config/event correlation |
| Entity Index | 连接 service、region、cluster、owner | 依赖命名规范和 metadata 质量 | cross-source joining |
| Keyword Index | 精确、可解释、低延迟 | 语义泛化弱 | error code, config key, request ID |
| Dense Vector Index | 语义召回强 | 对精确 token 弱，解释性差 | similar incidents, natural language docs |
| Sparse / Hybrid Vector | 兼顾语义和 token 贡献 | 需要调参和 score fusion | RCA knowledge search |
| Graph Index | 支持多跳依赖推理 | 图构建和更新成本高 | fault propagation |
| Structured Document Index | 精确定位文档章节 | 依赖文档结构质量 | runbooks, SOPs, policies |
| Incident Memory Index | 复用同一事故窗口上下文 | 有记忆污染风险 | multi-alert incident handling |

核心原则：

> RCA 系统不要把所有东西都塞进一个向量库，而应该采用 typed multi-index + query router + evidence fusion。

---

# 4. Document Understanding：把运维文档变成可推理知识

Document Understanding 不是一个独立功能，而是 ingestion pipeline 的关键部分。它主要用于：

- runbooks；
- postmortems；
- incident tickets；
- deployment notes；
- architecture docs；
- policy documents；
- compliance documents；
- design docs。

它可以分为四层：结构理解、semantic chunking、信息抽取和上下文关联。

---

## 4.1 结构理解：识别文档功能区块

结构理解的目标是识别文档中的功能区块，例如：

- symptom；
- diagnosis；
- mitigation；
- rollback；
- safety warning；
- escalation；
- root cause；
- timeline；
- follow-up action。

例如，一个 runbook 可能包含：

```text
Symptoms
Diagnosis Steps
Mitigation
Rollback Conditions
Safety Constraints
Escalation Policy
```

如果 Agent 问：

> Can we safely restart this service?

系统不应该只是找包含 “restart” 的文本，而应该优先定位到：

```text
Runbook → Mitigation → Restart Procedure
Runbook → Safety Constraints → Restart Conditions
```

因为在自动恢复场景里，安全规则通常比操作步骤本身更重要。

---

## 4.2 Semantic Chunking：按完整语义单元切分

传统 chunking 可能只是每 500 或 1000 个 token 切一段。但在运维场景中，这可能造成风险，因为一个完整操作步骤或 safety warning 可能被切断。

Semantic chunking 的目标是按照完整语义单元切分，例如：

- 一个 symptom chunk；
- 一个 diagnosis procedure chunk；
- 一个 mitigation procedure chunk；
- 一个 rollback warning chunk；
- 一个 escalation policy chunk。

例如，一个 Spark job failure runbook 可以被切成：

```text
Chunk 1: Symptom - Spark driver failed
Chunk 2: Diagnosis - Check pod event, service account, S3 access
Chunk 3: Mitigation - Refresh credentials or rollback config
Chunk 4: Safety Warning - Do not retry repeatedly before validating credentials
Chunk 5: Escalation - Contact platform team if STS errors persist
```

这样 Agent 检索到的是完整、可操作、上下文明确的信息单元，而不是碎片化文本。

### Tradeoff

| Chunking 方式 | 优点 | 缺点 |
|---|---|---|
| Fixed-size chunking | 简单，容易实现 | 容易切断操作步骤或安全约束 |
| Heading-aware chunking | 保留文档结构 | 对格式不规范文档效果下降 |
| Semantic chunking | 上下文完整，适合 runbook | 实现更复杂，可能需要模型辅助 |
| Page/tree-based chunking | 可解释性强，适合长文档 | 对实时日志不适用 |

建议第一版采用：

> heading-aware chunking + metadata enrichment + limited semantic splitting

不要一开始就完全依赖 LLM 自动切分所有文档。

---

## 4.3 信息抽取：从非结构化文本提取结构化字段

信息抽取是把非结构化或半结构化文本转成结构化字段。

从 logs 中可以抽取：

- service name；
- error type；
- endpoint；
- status code；
- latency；
- request ID；
- region；
- account ID；
- pod name。

从 deployment notes 中可以抽取：

- changed service；
- version；
- commit ID；
- rollout region；
- config key changed；
- owner；
- rollback plan。

从 postmortems 中可以抽取：

- symptom；
- impact；
- root cause；
- mitigation；
- prevention action；
- time to recovery。

从 runbooks 中可以抽取：

- trigger condition；
- diagnostic command；
- safe action；
- unsafe action；
- rollback condition；
- escalation owner。

这些抽取结果可以进入：

- metadata DB；
- keyword search index；
- vector index；
- graph index；
- policy engine。

### Deterministic Parser vs LLM Extraction

| 方法 | 适合内容 | 优点 | 风险 |
|---|---|---|---|
| Regex / parser | timestamp, error code, ID, service name | 稳定、可控 | 对格式漂移敏感 |
| Log template extraction | 结构化日志模板 | 适合大规模日志聚合 | 需要维护模板或在线学习 |
| LLM structured extraction | runbook, postmortem, incident notes | 对自然语言理解强 | 需要 validation，不能直接信任 |
| Hybrid extraction | 关键字段用 parser，自然语言用 LLM | 最稳妥 | 实现复杂度较高 |

生产系统中，关键字段如 timestamp、service、region、error code、request ID 应尽量用 deterministic logic 抽取。LLM 更适合抽取 symptom、root cause、mitigation、risk warning 这类自然语言信息。

---

## 4.4 上下文关联：把证据连成因果链

上下文关联是 RCA 的核心。

例如：

```text
10:01 - workspace-service deployment started
10:04 - database latency increased
10:05 - API error rate increased
10:06 - logs show connection timeout
Historical incident - similar pattern caused by connection pool config
Runbook - check pool size before rollback
```

单独看每条信息都不够，但关联起来可以形成一个候选根因：

> Recent deployment may have introduced a database connection pool configuration issue.

这就是 Cross-Source Risk Intelligence Engine 的核心能力：不是看单个 alert，而是跨 logs、metrics、traces、deployment、config、history 和 runbook 形成证据链。

---

## 4.5 Evidence Pack：不要把原始索引直接暴露给 Agent

一个重要工程原则是：Agent 不应该直接面对原始搜索结果，而应该接收一个结构化的 **Evidence Pack**。

Evidence Pack 可以包含：

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

Evidence Pack 的好处是：

- 控制 LLM 输入质量；
- 降低 token 成本；
- 保留证据来源；
- 支持审计；
- 支持回归测试；
- 方便 Critic 检查支持证据和反证。

---

# 5. Vectorless RAG：基于结构导航的检索方式

## 5.1 Vectorless RAG 是什么

传统 RAG 通常依赖 embedding 和 vector database。流程大致是：

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

这种方式的核心是：

> 通过语义相似度找到相关文本。

Vectorless RAG 的思路不同。它不主要依赖 vector similarity，而是通过文档结构进行导航。流程更像：

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

它的核心目标不是找到“相似文本”，而是找到“正确位置”。

例如，对于一个 runbook，问题不是：

> 哪个 chunk 和 rollback 这个词最相似？

而是：

> rollback 的安全条件在哪一节？  
> database migration 相关 warning 在哪里？  
> escalation policy 在哪里？

这类问题更适合结构化导航。

---

## 5.2 Vectorless RAG 适合什么

Vectorless RAG 特别适合长结构化文档，例如：

- runbooks；
- SOPs；
- postmortems；
- architecture docs；
- compliance docs；
- security policies；
- deployment playbooks；
- operation manuals。

这些文档通常天然有层级结构：

```text
Document
 ├── Section
 │    ├── Subsection
 │    └── Table
 └── Appendix
```

当问题可以被映射到某个文档位置时，结构化导航通常比相似度检索更稳定。

例如：

> Can I restart this service safely?

更合理的 retrieval path 是：

```text
Runbook
  → Mitigation
  → Restart Procedure
  → Safety Constraints
```

而不是只找包含 “restart” 的相似 chunk。

---

## 5.3 Vectorless RAG 不能替代什么

Vectorless RAG 有价值，但不能替代整个 RCA 系统。

它不能替代：

- log search；
- metrics query；
- distributed tracing；
- deployment / config metadata；
- service dependency graph；
- root cause scoring；
- policy verification。

原因是 RCA 系统面对的不只是长文档，还包括大量实时、半结构化、高频数据，例如：

- raw logs；
- metrics time series；
- trace spans；
- Kubernetes events；
- deployment events；
- configuration changes；
- high-cardinality operational metadata。

这些数据更适合使用：

- Elasticsearch / OpenSearch；
- Prometheus / CloudWatch；
- Jaeger / Tempo；
- metadata DB；
- graph database；
- stream processing。

所以 Vectorless RAG 更适合作为 **structured knowledge navigation layer**，而不是替代 observability search。

---

## 5.4 在 RCA Agent 中如何使用 Vectorless RAG

在 RCA Agent 中，Vectorless RAG 可以用于检索结构化运维知识。

例如：

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

其中 Vectorless Structured Knowledge Retrieval Tool 主要负责：

- runbook diagnosis section；
- rollback safety section；
- escalation policy；
- architecture dependency description；
- compliance requirement；
- security operation policy。

它帮助 Agent 找到正确章节，而不是只找到相似文本。

---

# 6. PageIndex-style Retrieval：层级文档索引与精确章节检索

## 6.1 PageIndex-style 是什么

PageIndex-style retrieval 是一种基于文档结构的检索思路。它的核心思想是：

> 先为文档建立类似 Table of Contents 的层级结构索引，然后根据 query 在树状结构中进行导航，定位最相关的 section、subsection 或 paragraph。

它和传统 vector RAG 的区别在于：

- 传统 vector RAG 依赖 chunk + embedding + similarity search；
- PageIndex-style retrieval 更强调 document structure、hierarchical navigation 和 precise section retrieval。

它适合处理长文档，尤其是那些结构清晰、章节明确、需要精确引用的文档。

例如：

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

对于问题：

> Is rollback safe after database migration?

PageIndex-style retrieval 可以导航到：

```text
Runbook
  → Mitigation
  → Rollback Service
  → Safety Constraints
  → Database Migration Warning
```

这比单纯返回几个相似 chunk 更适合安全决策。

---

## 6.2 PageIndex-style 的离线索引流程

PageIndex-style retrieval 通常需要一个离线或准实时的 indexing pipeline。

流程可以是：

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

其中 metadata 很重要，例如：

- service；
- system；
- doc_type；
- section_type；
- owner；
- updated_at；
- risk_level；
- environment；
- related incident；
- related dependency。

这些 metadata 可以帮助 Agent 在 incident-time 做 query routing 和 section filtering。

---

## 6.3 PageIndex-style 的在线检索流程

当事件触发或 on-call engineer 提问时，Agent 可以调用 structured retrieval tool。

例如：

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

最终返回的结果可以包含：

- 精确章节内容；
- 文档路径；
- section path；
- 更新时间；
- risk warning；
- applicable conditions。

例如：

```text
Retrieved Evidence:
Runbook → Workspace Service → Deployment Recovery → Rollback Conditions

Rule:
Rollback is only safe when the schema migration is backward compatible
and no active migration job is running.
```

这种 retrieval path 对 auditability 很有价值。因为系统可以解释：

> 我为什么检索到这条规则，以及它来自文档的哪个位置。

---

## 6.4 PageIndex-style 方法如何应用到 RCA Agent

PageIndex-style 方法可以作为 RCA Agent 的 **Structured Knowledge Retrieval** 模块。

整体系统可以是：

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

PageIndex-style retrieval 主要处理：

- runbooks；
- postmortems；
- architecture docs；
- operation manuals；
- security policies；
- compliance docs；
- deployment playbooks。

它不负责 raw logs、metrics、traces 或实时事件流。

---

# 7. Hybrid RCA Retrieval：不是 Vector vs. Vectorless，而是组合使用

## 7.1 为什么需要 Hybrid Retrieval

在生产 RCA 场景中，不同数据类型适合不同的检索方式。

| 数据类型 | 最适合的方法 |
|---|---|
| Raw logs / stack traces | Elasticsearch / OpenSearch keyword search |
| Metrics | Prometheus / CloudWatch time-series query |
| Traces | Jaeger / Tempo / APM trace query |
| Deployment / config records | Relational DB + metadata index |
| Historical incidents | Keyword search + vector semantic search |
| Runbooks / SOPs | Structured document navigation |
| Service dependencies | Graph index / service catalog |
| Safety policies | Structured retrieval + policy engine |

因此，最合理的架构不是只用 vector，也不是完全 vectorless，而是：

```text
Hybrid RCA Retrieval
= Observability Search
+ Keyword Search
+ Vector Semantic Search
+ Structured Knowledge Navigation
+ Dependency Graph
+ Evidence Ranking
```

每类数据使用最适合的方法。

---

## 7.2 Query Routing：不同问题走不同索引路径

RCA Agent 的一个关键能力是 query routing。不同问题应该查不同的数据源。

| Query 类型 | 应该查询的数据源 |
|---|---|
| 为什么 error rate 上升？ | logs, metrics, traces, deployment index |
| 是否可以 rollback？ | deployment history, runbook safety section, policy verifier |
| 有没有类似历史事故？ | incident history, vector search, keyword search |
| 谁 owns 这个 service？ | service catalog, metadata DB |
| 这个 error 是什么原因？ | logs, runbook diagnosis, historical incidents |
| 这个 action 安全吗？ | safety constraints, dependency graph, policy verifier |

第一版可以用简单规则实现：

```text
if query contains "safe", "rollback", "restart":
    route to runbook safety sections + deployment index + policy checker

if query contains "similar", "happened before":
    route to incident history + vector search

if query contains "why", "root cause":
    route to logs + metrics + traces + deployment + dependency graph
```

后续可以让 LLM agent 根据问题动态生成 search plan。

---

## 7.3 Late Fusion 与 Reranking

Hybrid retrieval 的难点不是“同时查多个索引”，而是如何融合多个索引结果。

例如，一个 candidate evidence 可能来自：

- BM25 keyword score；
- dense vector similarity；
- sparse vector score；
- time proximity；
- entity match；
- graph distance；
- document section relevance。

这些分数尺度不同，不能直接相加。因此需要：

1. score normalization；
2. source weighting；
3. top-N candidate pooling；
4. reranking；
5. evidence pack construction。

一个简单 late fusion 方式：

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

| 策略 | 优点 | 缺点 |
|---|---|---|
| Early fusion | 查询快，流程简单 | 很难统一不同模态 |
| Late fusion | 灵活，可解释 | 需要 score normalization |
| Learned reranker | 效果可能更好 | 需要训练数据和在线评估 |
| Rule-based reranker | 可控，适合 MVP | 需要人工调权重 |

MVP 阶段建议先用 rule-based late fusion，等积累足够 incident replay 数据后，再训练 learned reranker。

---

# 8. RCA Workflow：从事件触发到候选根因

## 8.1 事件触发方式

RCA Agent 可以由多种方式触发：

- monitoring alert；
- on-call engineer chat question；
- incident ticket；
- deployment canary failure；
- SLO burn rate alert；
- customer impact signal。

例如，on-call engineer 问：

> Why is workspace-service error rate increasing in us-east-1?

Agent 不应该直接回答。它应该先构建 incident context：

- service = workspace-service；
- region = us-east-1；
- symptom = error rate increasing；
- time window = last 30 minutes；
- environment = production。

然后生成 search plan。

---

## 8.2 Evidence Retrieval：多工具检索证据

Agent 可以调用不同工具：

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

这一步的目标不是马上得出结论，而是收集足够证据。

---

## 8.3 Time-Series Retrieval：把时序模式也纳入 RCA

传统 RAG 主要处理文本，但基础设施事故中很多早期信号来自时序指标，例如：

- CPU utilization；
- memory pressure；
- disk I/O；
- network throughput；
- request latency；
- error rate；
- queue depth；
- DB connection count；
- pod restart count。

因此，RCA Agent 不应该只做文本检索，也需要 **time-series retrieval**。

一种可行做法是：

1. 对当前 incident window 提取 metric pattern；
2. 从历史 incident 中检索相似时间序列片段；
3. 对比这些历史片段对应的 root cause；
4. 把结果作为 candidate evidence。

例如：

```text
Current pattern:
  DB latency rises first
  API error rate rises 2 minutes later
  CPU remains normal

Historical similar pattern:
  Incident #123
  Root cause: connection pool saturation after config change
```

这可以帮助 Agent 不只依赖日志文本，而是利用指标趋势进行 RCA。

### Tradeoff

| 方法 | 优点 | 缺点 |
|---|---|---|
| 简单阈值/变点检测 | 快、易解释 | 只能发现异常，不擅长归因 |
| 相似时序片段检索 | 可复用历史 incident 模式 | 需要高质量历史标签 |
| TSFM / TS-RAG | 对复杂趋势更强 | 工程复杂度高，适合后期增强 |
| 规则 + 统计 + 检索结合 | MVP 最现实 | 需要持续调参 |

MVP 中可以先实现：

> change-point detection + historical metric pattern search + evidence pack integration

不需要一开始就训练或部署复杂时间序列基础模型。

---

## 8.4 Evidence Synthesis：形成证据链

检索后，系统可能得到：

```text
10:01 - workspace-service deployment started
10:04 - metadata-db latency increased
10:05 - workspace-service error rate increased
10:06 - logs show database connection timeout
Historical incident - similar pattern caused by connection pool config
Runbook - check connection pool before rollback
```

Agent 可以把它整理成证据链：

> The error increase started shortly after deployment. The affected service depends on metadata-db. Metrics show database latency increased before the API error rate spike. Logs show connection timeout. A similar historical incident was caused by connection pool configuration. Therefore, a deployment-related DB connection configuration issue is a strong candidate root cause.

---

## 8.5 Critic 与 Counterfactual Validator：加入反证机制

RCA Agent 不能只生成“看起来合理”的根因，还需要主动寻找反证。

可以增加一个 Critic / Counterfactual Validator，专门检查：

- 是否有反证？
- 是否有其他更合理的根因？
- 当前证据是否只是相关，不是因果？
- 如果假设反过来，结论是否还成立？
- 如果没有这次 deployment，异常是否仍可能发生？
- 如果 database 是根因，为什么其他依赖 database 的服务没有异常？

例如：

```text
Hypothesis:
  Recent deployment caused DB connection pool issue.

Counterfactual checks:
  1. Did the same error occur before deployment?
  2. Are services not touched by the deployment also affected?
  3. Did rollback or config revert improve metrics?
  4. Is the DB latency global or only visible from this service?
```

Critic 的输出不应该只是“同意/不同意”，而应该输出：

```json
{
  "hypothesis": "Deployment introduced DB config issue",
  "supporting_evidence": ["deployment at 10:01", "DB timeout logs", "similar incident"],
  "conflicting_evidence": ["other DB clients are normal"],
  "missing_evidence": ["need config diff", "need trace sample"],
  "confidence_adjustment": "-0.10"
}
```

这种机制可以减少 LLM hallucination 和 reasoning drift。

---

# 9. Ranking：如何排序证据和候选根因

## 9.1 Evidence Ranking

RCA Agent 检索到的证据可能很多，不能全部交给 LLM。需要先做 Evidence Ranking。

一个简单的 scoring function 可以是：

```text
evidence_score =
  0.25 * time_proximity_score
+ 0.20 * entity_match_score
+ 0.20 * text_relevance_score
+ 0.15 * semantic_similarity_score
+ 0.10 * source_reliability_score
+ 0.10 * severity_score
```

各项含义如下：

| Score | 含义 |
|---|---|
| time_proximity_score | 证据是否接近 incident start time |
| entity_match_score | 是否匹配 service、region、cluster、account |
| text_relevance_score | keyword/BM25 相关性 |
| semantic_similarity_score | embedding 相似度 |
| source_reliability_score | 来源是否可靠，例如 official runbook 高于聊天记录 |
| severity_score | 是否为 critical alert 或 high-severity error |

例如，一个 deployment 发生在 incident 前 3 分钟，且影响同一个 service 和 region，它的 time/entity score 会很高。一个两周前的无关 deployment 则应该排在后面。

---

## 9.2 Evidence Ranking 的增强维度

除了基础 score，还可以加入 RCA 特有的维度：

```text
evidence_score =
  base_retrieval_score
+ change_relevance_score
+ topology_relevance_score
+ freshness_score
+ contradiction_penalty
+ safety_priority_boost
```

其中：

- `change_relevance_score`：证据是否和最近变更相关；
- `topology_relevance_score`：证据是否位于依赖路径上；
- `freshness_score`：索引是否足够新；
- `contradiction_penalty`：是否与其他证据冲突；
- `safety_priority_boost`：如果是 safety constraint，应提高优先级。

例如，当用户问“是否可以 rollback”，即使某个 safety warning 的语义相似度不是最高，也应该因为 section_type = safety_constraint 而提升排名。

---

## 9.3 Root Cause Ranking

Evidence ranking 之后，需要对 candidate root causes 排序。

一个 root cause scoring function 可以是：

```text
root_cause_score =
  0.30 * supporting_evidence_strength
+ 0.20 * temporal_causality
+ 0.20 * dependency_path_match
+ 0.15 * historical_similarity
+ 0.10 * blast_radius_match
+ 0.05 * absence_of_contradiction
```

例如：

### Candidate 1: Recent deployment introduced DB config issue

支持证据：

```text
deployment happened 3 minutes before incident
same service affected
DB connection timeout increased
historical incident had similar pattern
runbook recommends checking connection pool config
```

这个 candidate 分数较高。

### Candidate 2: Database global outage

支持证据：

```text
DB latency increased
```

反对证据：

```text
only one service affected
other DB clients normal
```

这个 candidate 分数中等或较低。

### Candidate 3: Network outage

支持证据：

```text
some timeout logs
```

反对证据：

```text
no other services in same region affected
no network-level alerts
```

这个 candidate 分数较低。

第一版不需要特别复杂。MVP 可以先用规则和权重，后续再加入 learned reranker、causal graph 或 anomaly detection model。

---

## 9.4 输出中必须包含反证和不确定性

为了避免 Agent 过度自信，RCA 输出不应该只包含“最可能根因”。更好的格式是：

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

这比单纯输出自然语言结论更适合生产 RCA。

---

# 10. RCA 不是单一模型，而是 Evidence-Grounded Pipeline

## 10.1 不建议一开始训练 RCA 大模型

RCA 不应该被理解成一个单一模型。更可行的方式是把 RCA 做成一个 pipeline：

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

第一版可以采用：

```text
Rule-based correlation
+ Hybrid retrieval
+ LLM reasoning
+ Policy verification
```

也就是说，不是训练一个“RCA 大模型”，而是构建一个 **evidence-grounded RCA pipeline**。

---

## 10.2 LLM 在 RCA Pipeline 中的作用

LLM 可以负责：

- 生成 search plan；
- 根据 incident context 决定调用哪些 tools；
- 总结检索到的证据；
- 生成 candidate root causes；
- 解释证据链；
- 根据 runbook 提出 next action；
- 把结果转成 on-call engineer 可以理解的语言。

但是，关键逻辑不应该完全依赖 LLM。例如：

- timestamp parsing；
- service metadata join；
- region / cluster / account filtering；
- deployment lookup；
- permission check；
- policy validation；
- high-risk action approval；
- command allowlist。

这些更适合 deterministic logic 或 policy engine。

---

## 10.3 检测与定位层可以作为可替换 Tool

RCA pipeline 中的 detection / localization 不需要只有一种算法。更合理的做法是把不同算法封装为 tools：

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

这样 Agent 不需要自己“学会所有 RCA 算法”，而是负责编排这些工具。

### Tradeoff

| 方法 | 优点 | 缺点 |
|---|---|---|
| 统计/变点检测 | 快、稳定、可解释 | 只能定位异常，不一定能归因 |
| 因果图 / 贝叶斯网络 | 可解释，适合表达不确定性 | 依赖图质量和先验 |
| GNN / 在线因果学习 | 能处理复杂传播 | 训练和部署成本高 |
| Graph-free fallback | 图缺失时可用 | 因果链表达弱 |
| LLM synthesis | 表达能力强 | 必须依赖证据和验证器 |

推荐方式是 ensemble：

> change-point detection → candidate generators → evidence pack → critic validation → root cause ranking

---

# 11. MVP 架构：如何实际落地

## 11.1 可落地的技术栈

一个实际可行的 MVP 可以这样设计：

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

MVP 目标可以定义为：

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

## 11.3 性能与可扩展性设计

RCA 系统的性能瓶颈通常不在 LLM，而在：

- index write throughput；
- log time range scan；
- vector memory；
- trace search；
- graph traversal；
- cross-modal fan-out；
- stale cache；
- score fusion latency。

因此，建议采用：

```text
Hot / Warm / Cold Storage
+ Summary Index
+ Incident Evidence Cache
+ Modality-specific Scaling
```

### Hot / Warm / Cold 设计

| 层级 | 内容 | 目标 |
|---|---|---|
| Hot | 最近 1-7 天完整 logs/traces/vectors | 低延迟 RCA |
| Warm | 最近 1-4 周压缩数据 | incident replay / trend analysis |
| Cold | 长期 RCA summaries / rollups | 低成本历史学习 |
| Summary Index | incident summary, root cause, mitigation, embedding | 快速相似事故检索 |

### Evidence Cache

对于同一 incident window，可以缓存：

- query plan；
- service graph；
- top evidence；
- candidate causes；
- runbook sections；
- policy decisions。

这样可以避免多个 alerts 对同一事故重复 fan-out。

---

## 11.4 索引新鲜度和一致性

多索引系统最大的风险之一是 freshness 不一致。

例如：

- logs 已经进了 OpenSearch；
- deployment event 还没进 DB；
- vector index 还没更新；
- service graph 仍是旧拓扑；
- runbook 刚更新但 structured index 未刷新。

这可能导致 Agent 做出错误判断。

缓解方式：

1. 所有 evidence item 带上 `indexed_at` 和 `source_updated_at`；
2. Evidence Pack 标记 freshness；
3. 高风险 action 前强制查询实时 API；
4. 使用 append-only event stream；
5. 对文档使用 versioned document IDs；
6. 对最终 RCA 记录使用证据版本。

例如输出中可以包含：

```text
Freshness warning:
  Deployment index is fresh within 30 seconds.
  Runbook index was last updated 2 days ago.
  Service graph snapshot is 15 minutes old.
```

这对生产系统非常重要。

---

# 12. Core Design Principles

## 12.1 不要让 LLM 直接看日志猜答案

更安全的方式是：

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

## 12.2 不要只用 Vector DB

运维 RCA 需要 hybrid retrieval：

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

## 12.3 Vectorless RAG 和 PageIndex-style 是结构化知识检索层，不是整个 RCA 系统

它们适合：

- runbooks；
- postmortems；
- SOPs；
- architecture docs；
- policy docs。

它们不适合替代：

- logs；
- metrics；
- traces；
- deployment metadata；
- service dependency graph；
- policy verification。

---

## 12.4 RCA 不应是黑盒模型

第一版更可行的方式是：

```text
Evidence-grounded RCA pipeline
```

后续再逐步引入：

- anomaly detection；
- causal graph；
- learned reranker；
- incident similarity model；
- time-series retrieval；
- automated remediation verifier。

---

## 12.5 执行动作必须从 LLM reasoning 中剥离

Agent 可以建议动作，但不应该自由生成 shell 命令或任意 API 调用。生产环境中，自动化执行应通过：

- Action Catalog；
- parameterized runbook；
- policy engine；
- approval workflow；
- pre-check；
- post-check；
- rollback path。

例如：

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

这能防止 Agent 把“诊断建议”误变成危险操作。

---

## 12.6 可解释性不是一句总结，而是 Evidence DAG

生产 RCA 的解释性不应该只是自然语言总结，而应该是可复核的证据图。

Evidence DAG 可以包含：

- query；
- tool call；
- result item；
- candidate cause；
- supporting evidence；
- conflicting evidence；
- policy decision；
- action result；
- post-check outcome。

例如：

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

这样 postmortem 时可以复盘：

- Agent 查了什么；
- 为什么查；
- 哪些证据支持结论；
- 哪些证据反驳结论；
- 为什么某个 action 被允许或阻止。

---

# 13. Evaluation：如何验证系统是否真的有效

一个 RCA Agent 不能只看“回答是否流畅”。需要从 retrieval、RCA、safety、latency、auditability 多维评估。

## 13.1 Retrieval Metrics

- Evidence Recall@5；
- MRR / nDCG；
- exact token retrieval accuracy；
- runbook section accuracy；
- similar incident retrieval accuracy；
- index freshness lag；
- p50 / p95 retrieval latency。

## 13.2 RCA Metrics

- AC@1；
- AC@3；
- top-k root cause coverage；
- time-to-first-useful-hypothesis；
- missing-modality robustness；
- graph corruption robustness。

## 13.3 Safety Metrics

- unsafe action suggestion rate；
- policy violation rate；
- manual override rate；
- rollback success rate；
- post-check pass rate；
- blast radius containment。

## 13.4 AgentOps Metrics

- tool call count；
- token cost；
- failed tool call rate；
- hallucinated evidence rate；
- citation precision；
- audit reconstruction time；
- critic correction rate。

## 13.5 Ablation Tests

建议做逐层 ablation：

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

观察每层对 RCA accuracy、latency、safety 的增量。

---

# 14. 结论

AI-driven remediation 的关键不只是模型能力，而是证据基础。一个可靠的 autonomous resilience system 必须先解决如何发现、索引、理解、关联和排序运维证据的问题。

对于生产级 RCA Agent，最合理的路线不是单纯的 vector RAG，也不是完全 vectorless，而是混合式架构：

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

这样的系统才能从“被动告警”走向“证据驱动的诊断”，再进一步走向“安全、可验证、可审计的自动化恢复”。

真正决定系统上限的，不是换一个更大的模型，而是把证据层做成：

- 分类型；
- 多模态；
- 时序感知；
- 变更感知；
- 可解释；
- 可审计；
- 可回放；
- 可验证。

这才是 AI Agent 在云原生基础设施自动诊断中真正可落地、可扩展、可进入生产系统的方向。
