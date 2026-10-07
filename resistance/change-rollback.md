# change-rollback — 变更必须先有回滚

## 触发范围

以下改动在给出**书面回滚方案**之前不得执行、不得建议执行：

- CORS：新增/删除允许源、开启 `Allow-Credentials`、改 `Vary: Origin`。
- 鉴权与会话：Cookie 属性、`SameSite`、域名/路径作用域、令牌算法与有效期、
  登出与吊销逻辑、OAuth 回调与 `redirect_uri` 匹配规则。
- 安全响应头：CSP 从 report-only 转 enforce、HSTS `max-age`/`preload`、
  `frame-ancestors`。HSTS preload 与 `includeSubDomains` 尤其难撤回。
- TLS 与证书：终止位置、协议版本下限、SNI/回源证书变更。
- 缓存键与 CDN：改 `Vary`、改 TTL、改 purge 范围、切 immutable 策略。
- 数据库：任何迁移、索引增删、读写路由切换。

## 回滚方案必须包含

1. 一条可直接复制执行的回滚命令或开关名（不是「重新部署上一版」这种描述）。
2. 触发阈值：指标 + 数值 + 观察窗口（如错误率 > 基线×3 持续 5 分钟）。
3. 数据是否可回滚：迁移默认**只向前修复**，若需回退必须证明 down 路径已演练。
4. 缓存清理范围与冷启动代价（回滚后短时间内的 origin 压力）。
5. 决策人与决策时限。
6. 演练记录：在 staging 上跑过一次，附时间戳与实测耗时。

模板见 [templates/rollback-plan.md](../asset/templates/rollback-plan.md)。

## 禁止

- 以「问题不大，先上了」跳过第 1、2 条。
- 把回滚与「再改一次」混为一谈（那是修复，不是回滚）。
- 在回滚路径里安排任何破坏性数据步骤 —— 见
  [data-change-guardrails](data-change-guardrails.md)。

## 违反后果

CORS/鉴权误配会让全站登录或跨域请求瞬间中断，且 HSTS 与 preload 一旦下发
即在客户端缓存期内不可撤回；无回滚方案的变更等于把停机时间交给运气。
