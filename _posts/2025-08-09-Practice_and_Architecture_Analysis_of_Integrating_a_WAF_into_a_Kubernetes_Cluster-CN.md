---
layout: post
title:  "在 Kubernetes 集群中集成 Web 应用防火墙（WAF）的实践与架构分析"
date:   2025-08-09
categories: jekyll update
tags: 
  - Kubernates
  - WAF
  - Security
lang: zh
---

{% include lang-switch.html %}

通过在 Kubernetes 集群中集成 Web 应用防火墙 (WAF)，过滤进入集群的恶意流量，保护对公网暴露的服务（如反向代理、API 网关、内容管理系统等），防止路径遍历、远程代码执行 (RCE)、爬虫扫描、凭证探测、拒绝服务 (DoS) 等攻击，减少后端资源占用并提高整体安全性。  
本篇以 **Wallarm WAF** 为例进行说明，但方法同样适用于其他 WAF 产品（如 AWS WAF、Cloudflare WAF、ModSecurity、F5 Advanced WAF 等）。

---

## 架构与组件职责

### 1. 外部服务（Wallarm 提供）
- **WAF API/Dashboard**：托管在 WAF 服务商云端，负责展示攻击可视化信息、流量统计、请求详情等。
- **Node 管理**：Dashboard 中的 Node 对应集群内的 WAF Ingress Controller 实例。每个 Node 在创建时生成唯一 Token，用于集群与 Dashboard 之间的安全通信。
- **WAF 规则与检测引擎**：根据内置规则实时识别恶意请求（如访问敏感文件路径、SQL 注入、XSS 等）。

### 2. 用户端基础设施
- **ELB（Elastic Load Balancer）**：对外暴露服务入口，将流量转发至集群内 Ingress Controller。
- **Managed Kubernetes 集群（如 EKS、AKS、GKE 等）**：承载被保护的业务应用与 Ingress Controller，由云厂商托管，负责集群的高可用、自动升级与基础设施运维。
- **镜像仓库（ECR、GCR、ACR 等）**：存储自定义构建的 WAF Ingress Controller 镜像（基于官方 NGINX Ingress Controller 或其他入口控制器进行定制）。

### 3. Kubernetes 内部资源
- **WAF Ingress Controller**：入口控制器的定制镜像，内嵌 WAF 模块实现安全检测与拦截。
- **数据采集组件（如 Wstore）**：与 Ingress Controller 一同部署，收集流量元数据并发送至 WAF API。
- **受保护的 Ingress 资源**：通过注解启用 WAF 检测与拦截功能。
- **业务工作负载**：对外提供服务的后端应用（如 API 服务、Web 前端、文件下载服务等）。

![Kubernetes WAF 架构]({{ '/assets/images/post_img/kubernetes_waf_integration_architecture.png' | relative_url }})

---

## 流量工作原理
1. 外部流量进入 ELB（或其他负载均衡器）。
2. ELB 将流量转发至集群内的 **WAF Ingress Controller**。
3. WAF 模块实时分析请求：
   - 恶意流量 → 立即返回 `403 Forbidden`，不进入后端服务。
   - 合法流量 → 正常转发到后端应用。
4. 数据采集组件（如 Wstore） 收集分析数据，发送至 WAF Dashboard。
5. Dashboard 提供攻击来源、类型、时间、IP、CVE 等可视化信息。

---

## 部署与配置步骤
> 以 Wallarm 为例，其他 WAF 产品可能提供 Operator、YAML Manifest、边缘代理或云前置等不同形态。

1. **获取 Helm Chart** 并提取默认 `values.yaml`。
2. **自定义关键配置**：
   - `enabled: true`
   - `token`: 从 Dashboard 获取的 Node Token
   - `apiHost`: Wallarm API 端点（例：`us1.api.wallarm.com`，与集群部署地域无关）
   - `nodeGroup`: 与 Dashboard 中的 Node 分组对应
3. **Ingress Controller 升级**：
   - 升级到与 WAF 兼容的版本（如 NGINX Ingress Controller 1.11.5），并修复旧版本安全漏洞。
4. **注解控制防护模式**：
   - `nginx.ingress.kubernetes.io/wallarm-mode: block`（拦截模式，默认 monitoring 仅监控）
   - `nginx.ingress.kubernetes.io/wallarm-application: <整数ID>`（区分不同应用/环境）
5. **部署镜像**：
   - 基于官方镜像构建自定义版本，推送至自有镜像仓库。
6. **安全管理 Token**：
   - 通过脚本或安全密钥管理服务（如 KMS/Secrets Manager/Sealed Secrets）配置，避免明文泄露。

---

## 流量控制与区分策略

- **Application ID 唯一性**：
  - 不同 Ingress/环境应使用不同 ID，避免数据混淆。尚需验证“相同 ID 跨环境”的具体行为。
- **Node 与 Token 管理**（两种常见做法）
  - **每环境单独 Node+Token**：强隔离，便于权限与可视化分区；
  - **单 Node + 多 Application ID**：管理简化，但需严格避免 ID 冲突。
- **白名单与限流**  
  对健康检查、版本接口等易被频繁访问的端点，可在 Ingress Controller 配置 **IP 白名单** 或 **速率限制 (Rate Limiting)**。这些为入口控制器通用能力，非 WAF 专属。

---

## 监控与功能验证

- **功能验证**：
  - 恶意请求 `GET /etc/passwd` → 成功拦截并返回 `403`
  - 合法请求（如 `/version`）→ 正常访问
- **Dashboard 可视化**：
  - 请求总数与速率
  - 恶意请求详情：类型、CVE、来源 IP、域名、目标路径
  - 按 Application ID 区分的流量视图
- **攻击源信息利用**：
  - 来源 IP 可用于在 ELB、防火墙等层面做进一步封锁或放行。

---

## 集成注意事项与挑战

1. **与现有部署流程冲突**：
   - 某些自动化流程可能会覆盖已部署的 **Ingress Controller**（需调整 `ingressClassName` 或部署逻辑，以避免升级/重建时被替换）。
2. **非 WAF 场景的保护**  
   - 即使有 VPN 与应用级 Token 的服务，也应监控潜在 bot 攻击流量，必要时结合入口层限流/ACL。
3. **许可与成本**：
   - 确认计费模式（按应用数/按流量/按规则包等），不同供应商有不同限制与套餐。
4. **合法请求的可用性保障**  
   - 对易被滥用端点应设置限流/熔断，防止放大效应导致后端资源耗尽。
5. **多环境/多集群一致性**  
   - 在每个环境/集群均需安装并配置入口控制器；可统一接入同一 WAF API，也可按环境分离。
