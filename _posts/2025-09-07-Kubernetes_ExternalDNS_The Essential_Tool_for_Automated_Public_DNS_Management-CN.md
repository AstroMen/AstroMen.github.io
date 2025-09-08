---
layout: post
title:  "Kubernetes ExternalDNS：自动化管理公网 DNS 的必备工具"
date:   2025-09-07
categories: jekyll update
tags: 
  - Kubernetes
  - DevOps
lang: zh
---

{% include lang-switch.html %}

在 Kubernetes 生产环境中，将服务暴露到公网是常态。我们通常通过 `Ingress` 或 `LoadBalancer` 类型的 `Service` 实现对外访问。然而，每当上线新服务或变更域名时，手动在云厂商 DNS 控制台添加 A 记录不仅效率低下，还容易出错。

有没有一种方式，能让 DNS 记录随着服务部署**自动创建、更新和清理**？答案就是：**ExternalDNS**。

> 🔗 GitHub 项目地址：[https://github.com/kubernetes-sigs/external-dns](https://github.com/kubernetes-sigs/external-dns)  
> 📚 官方文档：[https://external-dns.github.io/](https://external-dns.github.io/)

ExternalDNS 是由 Kubernetes SIGs 维护的开源控制器，它能**自动将集群内的 Service 和 Ingress 资源同步到外部 DNS 系统**（如 AWS Route 53、Cloudflare等），实现“服务即上线，域名即生效”的自动化流程。

---

## ExternalDNS 是什么？

ExternalDNS 是一个运行在 Kubernetes 集群中的控制器，它持续监听以下资源：

- `Ingress` 资源（最常用）
- `Service`（类型为 `LoadBalancer`）
- `Gateway`（支持 Kubernetes Gateway API）

当这些资源发生变化时，ExternalDNS 会提取其域名信息，并调用外部 DNS 提供商的 API，自动创建、更新或删除对应的 DNS 记录（A、CNAME、TXT 等）。

### 核心能力

- ✅ 自动同步 DNS 记录
- ✅ 支持主流云厂商和第三方 DNS 服务商
- ✅ 支持多集群、多租户隔离
- ✅ 基于注解（Annotations）灵活控制
- ✅ 可与 GitOps 流程无缝集成

---

## 工作原理

ExternalDNS 的核心流程如下：

1. 监听 Kubernetes 中的 `Ingress` 和 `Service` 资源  
2. 解析资源中的域名注解（如 `external-dns.alpha.kubernetes.io/hostname`）  
3. 获取服务的公网 IP（来自 LoadBalancer 或 Ingress Controller）  
4. 调用 DNS 提供商 API 创建/更新 A 记录  
5. 同时创建一条 TXT 记录用于所有权标识（防止冲突）  
6. 资源删除时自动清理 DNS 记录  

```
Ingress / Service  →  ExternalDNS Controller  →  Cloud DNS Provider  →  Public DNS Resolution
```

---

## 快速上手：以 AWS Route 53 为例

### 1. 安装 ExternalDNS（Helm）

我们推荐使用 Helm 安装，便于版本管理和配置维护。

> ✅ **明确版本信息（2025年9月最新稳定版）**

```bash
helm repo add external-dns https://kubernetes-sigs.github.io/external-dns/
helm install external-dns external-dns/external-dns \
  --version 1.19.0 \                    # 指定 Chart 版本（对应 appVersion v1.19.0）
  --namespace kube-system \
  --set provider.name=aws \
  --set aws.region=us-west-2 \
  --set txtOwnerId=my-cluster \
  --set domainFilters[0]=example.com \
  --set logLevel=info \
  --set policy=upsert-only              # 推荐生产环境使用
```

📌 **版本说明：**
- Helm Chart `1.19.0` 对应 ExternalDNS **应用版本 v1.19.0**
- Kubernetes 版本建议：**v1.22+**
- 更多版本信息见：[Helm Chart Releases](https://artifacthub.io/packages/helm/external-dns/external-dns)

---

### 2. 配置 AWS IAM 权限

ExternalDNS 需要权限操作 Route 53。若权限不足，将无法创建 DNS 记录。

#### 推荐 IAM Policy 示例：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets"
      ],
      "Resource": "arn:aws:route53:::hostedzone/YOUR_HOSTED_ZONE_ID"
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53:ListHostedZones",
        "route53:ListResourceRecordSets"
      ],
      "Resource": "*"
    }
  ]
}
```

> 🔐 **安全建议：**
> - 尽量使用 IAM Role 绑定给节点或使用 IRSA（IAM Roles for Service Accounts）
> - 避免使用长期 AccessKey
> - `ChangeResourceRecordSets` 是核心写权限，必须授予
> - `ListHostedZones` 用于查找匹配的托管区域

> 🔒 **生产环境推荐配置：`policy=upsert-only`**
>
> 默认行为 `sync` 会在资源删除时移除 DNS 记录。但在多租户或混合管理场景中，可能误删非本集群创建的记录。
>
> 使用 `--set policy=upsert-only` 后，ExternalDNS **只创建或更新记录，从不删除**，极大降低误操作风险。
>
> 删除操作需由其他机制（如 CI/CD 清理 Job）或人工完成。

---

### 3. 部署示例 Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    kubernetes.io/ingress.class: "nginx"
    external-dns.alpha.kubernetes.io/hostname: "app.example.com"
spec:
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
```

部署后，ExternalDNS 将自动：
- 获取 Nginx Ingress Controller 的 LoadBalancer IP
- 在 `example.com` 托管区创建 `app.example.com` 的 A 记录
- 在 `app.example.com` 同名位置创建一条 TXT 记录，内容包含：
  `"heritage=external-dns,external-dns/owner=my-cluster,external-dns/resource=ingress/my-app"`

---

## 深入理解：TXT 记录的作用

你可能注意到 ExternalDNS 会为每条 DNS 记录创建一个对应的 TXT 记录。它的作用是：

> 🔐 **所有权标识与防冲突机制**

当多个 ExternalDNS 实例（如多集群、多环境）管理同一个域名时，TXT 记录中的 `txtOwnerId` 字段用于标识该 DNS 记录的归属。ExternalDNS 在删除或更新记录前会先检查 TXT 记录是否匹配自己的 `txtOwnerId`，避免误删其他实例创建的记录。

📌 因此，在多集群场景下，务必为每个集群设置不同的 `txtOwnerId`，例如：

```bash
--set txtOwnerId=prod-cluster
--set txtOwnerId=staging-cluster
```

---

## 支持的资源与 DNS 提供商

### 支持的资源类型

| 资源 | 说明 |
|------|------|
| `Ingress` | 最常用，适合 HTTP/HTTPS 服务 |
| `Service` (LoadBalancer) | 直接暴露服务 IP，适合 TCP/UDP 服务 |
| `Gateway` (Kubernetes Gateway API) | 支持新一代网关标准 |

### 支持的 DNS 提供商

| 服务商 | 支持情况 |
|--------|----------|
| AWS Route 53 | ✅ |
| Google Cloud DNS | ✅ |
| Azure DNS | ✅ |
| Cloudflare | ✅ |
| DigitalOcean | ✅ |
| Alibaba Cloud | ✅ |
| CoreDNS (自建) | ✅ |
| PowerDNS | ✅ |

只需通过 `--set provider=xxx` 切换即可。

---

## 高级用法与最佳实践

### 1. 多域名支持

```yaml
external-dns.alpha.kubernetes.io/hostname: "web.example.com,api.example.com"
```

### 2. 自定义 TTL

```yaml
external-dns.alpha.kubernetes.io/ttl: "60"
```

### 3. 忽略某些资源

```yaml
external-dns.alpha.kubernetes.io/ignore: "true"
```

### 4. 手动指定目标（target）

适用于非 LoadBalancer 场景：

```yaml
external-dns.alpha.kubernetes.io/target: "1.2.3.4"
```

⚠️ **注意：**
- 技术上可以把 A 记录指向内网 IP（如 10.x.x.x），但公网客户端无法访问，通常无效
- 此功能更适用于 CNAME 或私有 DNS 场景
- 已知问题：在部分版本/配置下，如果 `policy=sync`，`target` 注解可能被忽略；建议搭配 `policy=upsert-only` 使用，更稳健

---

## 适用与不适用场景

| 场景 | 是否适用 | 说明 |
|------|---------|------|
| ✅ 公有云环境（AWS/GCP/Aliyun） | ✔️ | 最佳实践场景 |
| ✅ CI/CD 自动化部署 | ✔️ | 每次发布自动绑定域名 |
| ✅ 多环境（dev/stg/prod） | ✔️ | 配合 domainFilter 实现隔离 |
| ❌ 纯内网环境 | ⚠️ | 可用但需私有 DNS 支持（如 CoreDNS + 自建） |
| ❌ 域名由运维团队统一手工管理 | ❌ | 可能与现有流程冲突，需谨慎评估 |

---

## 调试与排错

### 1. 查看日志

```bash
kubectl logs -n kube-system deployment/external-dns
```

启用 Debug 日志获取更详细输出：

```bash
--set logLevel=debug
```

输出示例：

```
time="2025-04-05T10:00:00Z" level=debug msg="Adding DNS record: app.example.com -> 203.0.113.10"
time="2025-04-05T10:00:01Z" level=info  msg="Desired change: CREATE app.example.com A [Id: /hostedzone/Z12345]"
```

### 2. Dry-run 模式测试

首次部署建议使用 `--set dryRun=true`，--dry-run 为控制器级别的只演示模式，预览将要执行的操作而不实际修改 DNS。

### 3. 监控与可观测性（Prometheus Metrics）

ExternalDNS 内置 Prometheus 指标，暴露在 `/metrics` 端点（默认端口 `7979`）。

#### 常见指标包括：

| 指标 | 说明 |
|------|------|
| `external_dns_controller_sync_duration_seconds` | 同步周期耗时 |
| `external_dns_endpoint_count` | 当前管理的 DNS 记录数量 |
| `external_dns_registry_zone_records` | 每个托管区的记录数 |
| `external_dns_updates_total` | 成功更新次数 |
| `external_dns_update_failures_total` | 更新失败次数 |
| `external_dns_zones_count` | 管理的托管区数量 |

> 📊 **建议：**
> - 将 ExternalDNS 接入 Prometheus 抓取
> - 使用 Grafana 构建监控面板，观察 DNS 同步状态
> - 对 `update_failures_total` 设置告警，及时发现权限或网络问题

---

## Edge Cases 与注意事项

### 1. 泛域名支持

```yaml
external-dns.alpha.kubernetes.io/hostname: "*.example.com"
```

✅ 大部分 DNS 提供商支持  
⚠️ 但部分服务商（如 **Cloudflare**）对二级泛解析有限制（如不支持 `*.staging.example.com`）

### 2. Target 指向内网 IP

```yaml
external-dns.alpha.kubernetes.io/target: "10.0.0.1"
```

⚠️ **公网 DNS 虽然技术上允许将 A 记录指向私有 IP 地址，但对公网客户端无效**  
✅ 仅在私有 DNS 或内部解析场景中有意义（如 VPC 内部 CoreDNS）

---

## 总结

ExternalDNS 是 Kubernetes 环境中实现 **DNS 自动化管理**的关键组件。它通过声明式配置，将服务暴露与域名管理解耦，极大提升了 DevOps 效率。

### 核心价值

- 🚀 自动化：服务上线 = 域名生效
- 🔐 安全：通过 TXT 记录防止冲突，`upsert-only` 策略防误删
- 🧩 灵活：支持多云、多环境、多租户
- 📊 可观测：内置 Prometheus 指标，易于监控
- 🛠️ 易集成：与 Helm、GitOps、CI/CD 无缝协作

> 💡 **一句话 takeaway：**  
> **ExternalDNS = 声明式 DNS + 自动化运维**

> ✅ 推荐将其纳入标准 Kubernetes 发布流程，尤其适用于微服务、SaaS、CI/CD 密集型架构。

---

## 参考资料

- GitHub 项目：[https://github.com/kubernetes-sigs/external-dns](https://github.com/kubernetes-sigs/external-dns)
- 官方文档：[https://external-dns.github.io/](https://external-dns.github.io/)
- Helm Chart：[https://artifacthub.io/packages/helm/external-dns/external-dns](https://artifacthub.io/packages/helm/external-dns/external-dns)
- AWS IAM 权限参考：[Route 53 API Permissions](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/security_iam_service-with-iam.html)
- Prometheus Metrics 文档：[https://github.com/kubernetes-sigs/external-dns#metrics](https://github.com/kubernetes-sigs/external-dns#metrics)

---

*本文基于 ExternalDNS v1.19.0、Helm Chart 1.19.0、Kubernetes v1.22+ 编写，配置和行为可能随版本变化，请以官方文档为准。*
