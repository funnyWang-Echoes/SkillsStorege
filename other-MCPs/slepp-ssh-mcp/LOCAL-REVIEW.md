# LOCAL-REVIEW.md — slepp-ssh-mcp 入库审查记录

本文件记录本仓库对 `slepp-ssh-mcp` 的来源核验、实测验证与已确认问题，不涉及对上游代码的修改（入库副本与上游 `28834a8` 一致，仅剥离 `.github/` CI/发布 workflow 与 `.gitignore`）。

## 来源信息

| 项 | 内容 |
|---|---|
| GitHub | [slepp/ssh-mcp](https://github.com/slepp/ssh-mcp) |
| PyPI 包名 | `slepp-ssh-mcp`（用户口头的 “sleep-ssh-mcp” 实为本包名的误记，全网无 `sleep-ssh-mcp`） |
| 版本 / commit | v0.2.0 / `28834a8`（2026-07-09） |
| License | MIT |
| 作者 | Stephen Olesen（slepp，加拿大埃德蒙顿；GitHub 2008 年注册；另有 AX25 等真实项目） |
| 入库日期 | 2026-08-24 |

## 实测验证记录

| 项目 | 环境 | 结果 |
|---|---|---|
| 测试套件（`python3 -m unittest discover -s tests`） | WSL Ubuntu，Python 3.14.4 | 114/114 通过（35.9s） |
| 测试套件 | Windows 原生，Python 3.12.10 | 83 errors + 5 failures（根因：`os.openpty` 在 Windows 不存在，另有 fake-ssh 脚本 shebang/chmod 机制不兼容） |
| stdio 冒烟（`initialize` → `tools/list` → 关流退出） | WSL Ubuntu | 通过：`serverInfo={'name':'ssh-mcp','version':'0.2.0'}`，17 个工具，退出码 0 |

上游 CI 只测 ubuntu-latest + Python 3.10–3.13，与实测一致：**仅 POSIX 可用**。Windows 上须经 WSL 运行（如 `wsl -d Ubuntu -- uvx --from slepp-ssh-mcp ssh-mcp`）。

## 已确认的安全缺陷：`extra_ssh_args` 黑名单绕过

上游 README 的 Security 一节声称：`extra_ssh_args` 会拦截可触发**本机**命令执行的端口转发旗标（`-L`/`-R`/`-D`/`-W`）与危险 SSH 选项（`ProxyCommand`/`LocalCommand`/`LocalForward`/`RemoteForward`/`DynamicForward`）。代码中的黑名单为 `src/ssh_mcp/ssh.py` 的 `_BLOCKED_SSH_OPTIONS` / `_BLOCKED_SSH_SHORT_FLAGS` / `_BLOCKED_RSYNC_FLAGS`。

实测确认两条未覆盖的本机执行路径（在 WSL 中以 `ConnectionSettings.from_arguments` 直接复现）：

1. **`ssh -F <恶意config>`**：`-F` 不在黑名单，`extra_ssh_args=["-F","/tmp/evil_config"]` 通过校验并进入最终 argv。攻击者控制的 SSH config 可写 `ProxyCommand`/`LocalCommand`，由 ssh 在本机执行任意命令。
2. **`scp -S <恶意程序>`**：`-S` 不在黑名单，且 `ssh_scp` 把 `extra_ssh_args` 原样拼进 **scp** 的 argv（`build_transport_argv`）。scp 的 `-S program` 会用指定程序建立连接，即在本机直接执行该程序。复现输出：`['scp', '-S', '/tmp/evil_prog', ...]`。

严重度评估：**中等**。利用前提是 Agent 已能控制本机文件或二进制（写恶意 config / 准备恶意程序）。若 MCP client 本来就把本地 shell 交给 Agent，此缺口无额外意义；但若 client 依赖工具白名单做权限隔离（只暴露 SSH 工具），黑名单就未兑现其声明的保护。

处置状态：尚未向上游提 issue（对外动作，待用户决定）。已登记在根 `Readme.md` 后续待办。

## 其他已确认的限制（与上游 README 一致，此处只列影响使用方式的）

- **serve 循环单线程串行**（`src/ssh_mcp/server.py` 的 `serve()` 逐行读取、同步派发）：一个不设 `timeout` 的长 `ssh_exec` 会阻塞其他工具调用；会话本体在后台线程不受影响，但“长命令运行中同时读另一会话”做不到。
- **transcript 可能含敏感内容**（sudo 密码、输出中的密钥）：文件权限 0600、目录 0700，但会话结束后不自动清理，位于 `~/.local/state/ssh-mcp/`。
- **`ssh_edit` 非原子**：读-改-写为两次 SSH 往返，期间外部并发写入可能被覆盖（上游 README 已声明）。
- 远程文件工具按 UTF-8 `errors="replace"` 解码，二进制文件会出现替换字符（上游 README 已声明）。

## 使用建议

- 在 WSL/Linux/macOS 上以 `uvx --from slepp-ssh-mcp ssh-mcp` 接入；不要期望 Windows 原生可用。
- 若依赖工具白名单做权限隔离，在上游修复 `-F`/`-S` 绕过前，不要把 `extra_ssh_args` 暴露给不受信的 Agent 输入（部分 client 无法按参数粒度控制时，需知晓此残余风险）。
- 给会话起名（`session_name`）以便跨调用复用；长任务用会话而非无 timeout 的 `ssh_exec`。
