---
layout: post
title:  "Overview of JupyterHub"
date:   2024-01-26
categories: jekyll update
tags: 
  - JupyterHub
---

<p align="center">
    <br> 中文 | <a href="2024-01-26-Overview_of_JupyterHub.md">English</a>
</p>

JupyterHub 是一个多用户版本的 Jupyter Notebook，它允许许多用户在一个服务器上进行数据分析、科学计算等工作。以下是关于 JupyterHub 的综合指南。

## 1. JupyterHub 常用功能

JupyterHub 允许用户在不同设备上通过网络浏览器使用 Jupyter Notebook 环境。它具有以下常用功能：

- **多用户访问**：支持多个用户同时使用同一个服务器资源。
- **远程访问**：用户可以远程访问 JupyterHub 服务器上的 Notebook。
- **自定义环境**：每个用户都可以有一个独立的、定制化的计算环境。
- **资源分配**：管理员可以控制 CPU、内存等资源的分配。
- **安全性**：通过多种认证方式确保安全性。

## 2. JupyterHub 与 Jupyter Notebook 的对比

JupyterHub 和 Jupyter Notebook 都用于创建和分享包含实时代码的文档。它们的主要区别在于：

- **Jupyter Notebook** 是为单用户设计的，适合在个人电脑上使用。
- **JupyterHub** 允许多个用户通过服务器共享资源，适合于团队和教室环境。
- JupyterHub 的优点包括内置的用户管理、资源分配和安全性等功能。

## 3. JupyterHub 环境搭建

环境搭建主要包括安装、配置和启动 JupyterHub。这里是一个简单的命令序列，用于在 Ubuntu 系统上搭建环境：

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev npm nodejs
python3 -m pip install jupyterhub
npm install -g configurable-http-proxy
```

接下来，创建一个配置文件并编辑：

```bash
jupyterhub --generate-config
vim jupyterhub_config.py
```

在配置文件中，你可以设置例如认证方式、用户数据存储位置、日志文件的路径等选项。

要启动 JupyterHub，只需运行：

```bash
jupyterhub
```

这将启动 JupyterHub 服务并默认监听 8000 端口。

![JupyterHub 界面](https://raw.githubusercontent.com/ResearchComputing/Documentation/dev/docs/gateways/jupyterhub/jupyterlab1.png)

## 4. JupyterHub 的主要组件及其工作流程

JupyterHub 的工作流程涉及几个主要组件的协同工作：

- **Hub**：这是 JupyterHub 的核心，负责用户认证，以及启动和监控单用户 Jupyter Notebook 服务器。
- **Authenticator**：决定了用户如何登录。例如，PAM Authenticator 使用 Unix 的用户账户和密码，而 OAuthenticator 支持使用 OAuth 与外部服务进行认证。
- **Spawner**：负责启动用户的 Notebook 服务器。在 Cloud Kubernetes 环境中，KubeSpawner 可以用来在 Kubernetes 集群上动态创建和管理用户的 Notebook 服务器，提供灵活的资源管理和扩展性。
- **Configurable HTTP Proxy**：作为用户请求的入口点，负责将请求路由到正确的用户 Notebook 服务器。它根据用户的登录状态和请求的 URL，决定将请求发送到哪个服务器。
- **User Notebook Servers**：每个登录的用户都会有一个独立的 Notebook 服务器实例，这是用户进行所有工作的地方，包括编写代码、运行分析等。

### 工作流程
1. **用户访问**：用户通过浏览器访问 JupyterHub，请求被发送到 Configurable HTTP Proxy。
2. **用户认证**：请求被转发到 Hub，用户通过 Authenticator 登录。支持多种认证方式，包括 PAM、OAuth、LDAP 等。
3. **启动服务器**：认证成功后，Hub 会指示 Spawner 启动一个 Jupyter Notebook 服务器实例。如果是在 Kubernetes 环境中，KubeSpawner 会在 Kubernetes 集群中为用户启动一个单独的容器。
4. **代理请求**：一旦 Notebook 服务器启动，Configurable HTTP Proxy 会将所有指向该用户的请求路由到他们的服务器实例。
5. **用户交互**：用户可以开始在自己的 Jupyter Notebook 环境中工作，运行代码，创建和分享文档等。

![JupyterHub 组件](https://jupyterhub.readthedocs.io/en/stable/_images/jhub-parts.png)

## 5. JupyterHub 认证机制

### PAM 认证
- **功能描述**：使用 Linux 系统的 Pluggable Authentication Modules (PAM) 进行用户认证。
- **适用场景**：适用于所有用户都在 JupyterHub 服务器的系统中有账号的情况。
- **配置**：通常不需要特别配置，因为这是 JupyterHub 的默认认证方式。

### OAuth / OAuth2 认证
- **功能描述**：允许用户使用第三方服务（如 GitHub, Google）的账户进行认证。
- **适用场景**：适用于希望用户可以使用自己的社交账户登录的组织。
- **配置**：
  ```bash
  python3 -m pip install oauthenticator
  ```
  在 `jupyterhub_config.py` 文件中设置相应的 OAuth 回调 URL、客户端 ID 和客户端密钥。

### LDAP 认证
- **功能描述**：使用轻量级目录访问协议 (LDAP) 进行用户认证，通常与组织内部的用户目录服务集成。
- **适用场景**：适用于企业或教育机构，这些机构已经有 LDAP 服务器和用户数据库。
- **配置**：
  ```bash
  python3 -m pip install ldapauthenticator
  ```
  在 `jupyterhub_config.py` 文件中配置 LDAP 服务器的详细信息，包括地址、用户 DN 模板等。

### SAML 认证
- **功能描述**：使用安全断言标记语言 (SAML) 进行用户认证，适用于企业单点登录。
- **适用场景**：大型组织，需要与企业级身份提供商集成。
- **配置**：通常需要使用额外的库，如 `python3-saml`，并且配置过程比较复杂，需要设置实体 ID、断言消费服务 URL 等。

## 6. JupyterHub API

JupyterHub 的 API 提供了程序化方式管理和交互 JupyterHub。

### 主要功能
- **用户管理**：创建、更新和删除用户。
- **会话管理**：启动和停止用户的 Jupyter 服务器。
- **服务管理**：添加或删除 JupyterHub 服务。

### 使用 API 的步骤
1. 获取 API 令牌，通常在 JupyterHub 配置中指定或通过用户面板生成。
2. 使用 API 令牌发送请求到 JupyterHub 的 RESTful API 端点。

### 示例
获取当前所有用户的列表：
```bash
curl -H "Authorization: token <your_api_token>" https://<jupyterhub_url>/hub/api/users
```

## 7. JupyterHub 的测试套件

要安装 JupyterHub 的测试依赖并运行测试，可以使用以下命令：

```bash
python3 -m pip install --editable ".[test]"
pytest -vx jupyterhub
```

这些命令会安装所有测试依赖并运行 JupyterHub 的测试套件。

## 8. 配置 Nginx 作为反向代理到 JupyterHub

使用 Nginx 作为反向代理可以提高安全性，通过 SSL 证书加密数据，并提供负载均衡等高级功能。

### 配置步骤
1. **安装 Nginx**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```
2. **创建 Nginx 配置文件**
   配置文件通常位于 `/etc/nginx/sites-available/`。创建一个名为 `jupyterhub` 的配置文件：
   ```bash
   sudo touch /etc/nginx/sites-available/jupyterhub
   ```
3. **配置服务器块**
   编辑刚创建的配置文件 `/etc/nginx/sites-available/jupyterhub`，设置监听端口（如 80 或 443），并将请求代理到 JupyterHub：
   ```bash
   sudo vim /etc/nginx/sites-available/jupyterhub
   ```
   在文件中添加以下内容：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header Host $host;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
4. **启用站点并重启 Nginx**
   通过创建一个到 `/etc/nginx/sites-enabled/` 的软链接来启用站点：
   ```bash
   sudo ln -s /etc/nginx/sites-available/jupyterhub /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```
5. **配置 SSL（如果使用 HTTPS）**
   如果需要 HTTPS，可以使用 Let's Encrypt 提供的免费证书：
   ```bash
   sudo add-apt-repository ppa:certbot/certbot
   sudo apt install python-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```
   这会自动更新 Nginx 配置以使用 SSL，并定期自动更新证书。

## 9. 实际案例：多用户 JupyterHub 部署及 GitHub 用户认证

部署 JupyterHub 并使用 GitHub 认证需要以下步骤：

1. **在 GitHub 上注册 OAuth 应用**
   在 GitHub 设置中注册新应用，获取 `Client ID` 和 `Client Secret`。

2. **安装 `oauthenticator`**
   ```bash
   python3 -m pip install oauthenticator
   ```

3. **配置 JupyterHub 使用 GitHub 认证**
   编辑 `jupyterhub_config.py` 文件，添加 GitHub 认证器配置。
   ```python
   from oauthenticator.github import GitHubOAuthenticator
   c.JupyterHub.authenticator_class = GitHubOAuthenticator
   c.GitHubOAuthenticator.oauth_callback_url = 'https://your-domain.com/hub/oauth_callback'
   c.GitHubOAuthenticator.client_id = 'your-client-id'
   c.GitHubOAuthenticator.client_secret = 'your-client-secret'
   ```

4. **配置 Nginx 反向代理**
   按照前面的步骤配置 Nginx，确保它代理到 JupyterHub 并管理 SSL。

5. **启动 JupyterHub**
   ```bash
   jupyterhub
   ```

用户现在可以使用他们的 GitHub 账户来登录 JupyterHub 了。
