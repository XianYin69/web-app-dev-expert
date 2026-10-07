# secrets — 密钥与令牌红线

## 必须

1. 密钥、令牌、刷新令牌、数据库连接串、私钥、API key 一律来自运行时环境注入
   （secret manager、挂载文件、CI 密文变量），不得出现在仓库任何文件中。
2. `.env`、`*.pem`、`*.key`、`credentials.json` 必须在 `.gitignore` 内；
   提交前核对 `git status` 与 diff。
3. 日志序列化器使用**字段 allow-list**，不是敏感词 deny-list：
   默认丢弃 `Authorization`、`Cookie`、`Set-Cookie`、`X-Api-Key`、请求体。
4. 错误响应只回错误码与 trace id；堆栈、SQL、内部主机名、环境变量名一律不外泄。
5. 令牌落库只存哈希（refresh token、API key），并标注创建时间与轮换期限。
6. 一旦怀疑泄漏：立即吊销 → 轮换 → 清理历史（`git filter-repo` 或重写分支）→
   记录事件与影响面。

## 禁止

- 把真实密钥写进示例配置、README、测试夹具、提交信息、issue 或 PR 描述。
- 在 URL query 中传递令牌（会进访问日志与 `Referer`）。
- 用 `print`/`console.log` 调试时输出完整 header 或 payload。
- 把密钥放进镜像层（即使后续 `RUN rm`，层仍可读）。
- 为「临时方便」关闭脱敏中间件，或把脱敏等级降为 debug-only。

## 自检

- `python -B scripts/scan_dependency_vulns.py` 覆盖依赖面；
  密钥面用 `git log -p | Select-String -Pattern "(?i)(api[_-]?key|secret|token)\s*[:=]"`
  与专用扫描器复核。
- 探针 `scripts/check_response_headers.py` 会标记回显 `Set-Cookie` 的响应。

## 违反后果

凭据进入版本历史即视为已泄露（不可撤回），必须按第 6 条轮换并通知受影响方。
