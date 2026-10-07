# dependence — 依赖与分工

只引用名称与调用方式，不复制他技能正文。机器清单见 [deps.json](deps.json)
（每条含 `source_url` 原始链接；缺 `source_url` 即判不合格）。

## 兄弟技能（local://）

| 技能 | 何时移交 | 调用方式 |
|---|---|---|
| `web-design-expert` | 视觉、排版、交互、响应式断点设计 | `skill(name="web-design-expert", input=<设计诉求>)` |
| `frontend-dev` | 浏览器端框架实操（组件、状态、路由） | `skill(name="frontend-dev", input=<框架实操>)` |
| `interface-design-expert` | 接口契约本身的设计与命名评审 | `skill(name="interface-design-expert", input=<契约设计>)` |
| `database-management` | 库表设计、索引与查询调优深水区 | `skill(name="database-management", input=<库内诉求>)` |
| `concurrency-design` | 并发模型证明、锁与内存序分析 | `skill(name="concurrency-design", input=<并发分析>)` |
| `webapp-testing` | 端到端自动化测试编写与执行 | `skill(name="webapp-testing", input=<e2e 诉求>)` |
| `python-expert` | Python 语言级实现细节 | `skill(name="python-expert", input=<Python 问题>)` |
| `code-guidelines` | 静态审查规则与风格基线 | `skill(name="code-guidelines", input=<审查诉求>)` |

分工原则：本技能回答「服务端必须保证什么」；上述技能回答「那一层怎么做」。
跨界问题先在本技能定位到叶，再按表移交，禁止两边各写一遍正文。

## 软件依赖（software）

| 名称 | 用途 | 原始链接 |
|---|---|---|
| git | 版本控制与功能分支流 | <https://github.com/git/git> |
| node | 前端构建与探针脚本运行时 | <https://github.com/nodejs/node> |
| python | 探针脚本运行时（≥3.11） | <https://github.com/python/cpython> |
| curl | 响应头/预检/缓存手工复核 | <https://github.com/curl/curl> |
| openssl | TLS 与证书链复核 | <https://github.com/openssl/openssl> |

## 规范来源

见 [references](../references/references.md)（全部链接于 2026-10-07 本机核验 200）。
