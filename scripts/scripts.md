# scripts（脚本库）

web-app-dev-expert 的取证探针与红线自检。全英文文件名、仅用 Python 标准库、只读取被检
对象；写盘只允许 `tmp/`。执行：`python -B scripts/<name>.py <args>`（可离线 `--help`）。

## 探针（12 个 · 需真实目标才有结论）

| 脚本 | 取什么证（知识叶） | 入参 | 输出 / 退出码 |
|---|---|---|---|
| [`check_response_headers.py`](check_response_headers.py) | 安全响应头 HSTS/CSP/XFO/Referrer-Policy（4） | `--url` | `FINDING:` 行；0 干净 / 1 缺陷 / 2 不可达 |
| [`check_cookie_attrs.py`](check_cookie_attrs.py) | `Set-Cookie` 的 SameSite/Secure/HttpOnly（3） | `--url` | 同上 |
| [`check_tls_chain.py`](check_tls_chain.py) | 证书链、到期、协议版本（4/8） | `--host [--port]` | 同上 |
| [`probe_cors_preflight.py`](probe_cors_preflight.py) | 预检放行面是否过宽（4） | `--url --origin [--method] [--headers]` | 同上 |
| [`test_cache_compression.py`](test_cache_compression.py) | 压缩与再验证：`Vary`、ETag、`no-cache`≠`no-store`（1） | `--url` | 同上 |
| [`check_idempotency.py`](check_idempotency.py) | 同 `Idempotency-Key` 重放是否安全重演（1/7） | `--url [--method] [--body] [--header] [--key]` | 状态/摘要/Location 差异即缺陷 |
| [`check_api_contract.py`](check_api_contract.py) | 线上端点与声明契约面是否一致（2） | `--spec 清单 --base URL [--expect] [--header]` | 逐端点 OK/缺陷；全不可达 rc=2 |
| [`probe_injection_surface.py`](probe_injection_surface.py) | 输入回显与注入错误签名；`--src` 走源码静态面（4） | `--url [--param] [--src DIR]` | 命中签名即缺陷 |
| [`probe_open_redirect.py`](probe_open_redirect.py) | 重定向是否越出 allow-list（3） | `--url [--param] [--allow host,...] [--redirects]` | 越界即缺陷 |
| [`sample_web_vitals.py`](sample_web_vitals.py) | LCP/CLS/INP 风险因子；有 `--field` 才判阈值（9） | `--url [--field metrics.json]` | 只报因子，不编造数值 |
| [`report_bundle_budget.py`](report_bundle_budget.py) | 产物体积 vs 预算 route/vendor/css/fonts（9/5） | `--manifest m.json [--budget b.json] [--dir dist]` | 超标即缺陷 |
| [`scan_dependency_vulns.py`](scan_dependency_vulns.py) | lockfile → OSV 公告；`--offline` 仅解析（6/8） | `--lock <file> [--offline] [--top]` | 公告 ID；无法解析显式 `parse-skipped` |

## 自检（红线兜底 · 不需外部目标）

| 脚本 | 作用 | 调用 |
|---|---|---|
| [`check_links.py`](check_links.py) | 相对链接＋正文 `scripts/…` 等路径引用解析、`.md` ≤50 行、URL 形态；悬空必须为 0 | `python -B scripts/check_links.py --root . --strict-url` |
| [`deps_check.py`](deps_check.py) | `deps.json` 六字段齐备、`source_url` 为原始链接或 `local://` 且目标在位、`checked_at` 时效 | `python -B scripts/deps_check.py [--skills-root DIR]` |
| `_common.py` | 共用 `skill_root()`、文本遍历、统一 `RESULT PASS\|FAIL` 出口（非入口） | 被上述脚本 import |

## 约定

1. 输出统一：摘要行 → `FINDING: <证据>` → `RESULT PASS|FAIL (n)`；`--format json` 可选。
2. 退出码固定 0 干净 / 1 有缺陷 / 2 目标或输入不可用；解析失败显式 `parse-skipped`，不得当作通过。
3. 只读：探针不改写被检站点、被评审文件与他技能目录；缓存一律落用户缓存目录，技能目录内不得留 `__pycache__`。
4. 无凭据：不打印 cookie/token 值；需认证由调用方 `--header` 传入且不落盘。
5. 外部工具（Lighthouse/Playwright/bundler）只探在位性，缺失即降级为静态风险因子并注明。
