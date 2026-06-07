# CUA 分发与配置方案

日期：2026-06-07

## 结论

`scripts/python/run_multienv_cua_blackbox.py` 现在依赖本机可用的 CUA CLI 和 CUA config。这个依赖不能继续散在个人 `.env` 里瞎飘，后面要做成服务时，必须把它收口成一套可复用的 bootstrap 方案。

推荐的分层是：

1. 本地开发 / smoke 继续支持 `OSWORLD_CUA_BIN` 和 `OSWORLD_CUA_CONFIG_PATH` 直接指向本机路径。
2. 服务化 / ECS 部署使用私有 TOS 分发 CUA bundle，再在执行节点本地还原成 `cua_bin` 和 `cua_config_path`。
3. 黑盒 runner 本身不直接理解 TOS；TOS 下载、校验、解压、渲染配置都放在 runner 外层的 bootstrap 阶段。
4. 黑盒和 VM native 复用同一份 CUA bundle、同一套版本号、同一份 sha256 口径，只是安装位置不同。

也就是说，黑盒 runner 只认“本地路径”，但这些本地路径可以由服务侧从 TOS 动态准备出来。

## 范围

本文档只管三件事：

- CUA bundle 怎么打包、怎么上传。
- CUA config 怎么从本地语义源渲染成执行时配置。
- 执行节点怎么缓存、怎么恢复、怎么记录元数据。

不管这些内容：

- OSWorld case 本身怎么写。
- bridge 协议怎么映射。
- evaluator 怎么打分。
- 平台控制面 API 怎么调度。

## 统一原则

- CUA bundle 是不可变产物，走版本化、sha256 锁定。
- CUA config 不是原样上传物，必须先脱敏、再渲染、再落盘。
- TOS 里存的是可复现的构建产物，不存运行时密钥。
- 运行节点只保存本地安装副本和本地缓存，不保存 TOS AK/SK。
- `local_path` 只用于开发和单机 smoke，不作为生产默认。

## 产物拆分

### 1. CUA binary bundle

推荐继续复用 VM native 那边已经跑通的 Linux x64 bundle：

```text
bin/cua-linux-x64-pkg/
  cua-linux-x64.sh
  cua-linux-x64.cjs
  node_modules/
```

不要把下面这些东西混进正式 bundle：

- `bin/cua-darwin-arm64`
- `bin/cua-darwin-arm64.zip`
- 单独的 `cua-linux-x64.cjs`
- 未清理的 macOS xattr 和 `._*` 文件

原因很简单：黑盒 runner 最终跑的是 Linux 节点，bundle 必须和目标运行时一致。

### 2. CUA runtime config

config 不要原样上传本机 `config/local.json`。原始 config 里通常会带：

- 真实 API key。
- 本机绝对路径。
- 不适合服务节点的路径 / 坐标 / 目录语义。

推荐把 config 拆成两层：

- 语义源：本地 `config/local.json` 或一个专门的 `blackbox.runtime.template.json`。
- 运行时文件：执行节点上生成的 `~/.config/osworld-cua/blackbox.json`。

运行时文件必须把敏感字段改成环境变量占位符，例如：

```json
{
  "model": {
    "provider": "http",
    "baseURL": "${CUA_MODEL_BASE_URL}",
    "apiKey": "${CUA_MODEL_API_KEY}",
    "model": "${CUA_MODEL_NAME}"
  },
  "agent": {
    "runsDir": "/home/user/.local/share/osworld-cua-runs"
  }
}
```

## 上传方式

### bundle 发布

bundle 发布和 VM native 共用同一个发布脚本：

```bash
uv run python "scripts/python/publish_cua_vm_native_package.py" \
  --tos_bucket "evaluation-cua" \
  --env_output "./tmp_cua_release.env"
```

这个脚本负责：

- 干净打包。
- 计算 sha256。
- 上传私有 TOS。
- 生成短期 presigned URL 的检查用输出。
- 输出可直接喂给运行节点的 env 片段。

推荐的 object key 形式：

```text
cua/releases/cua-linux-x64-pkg-<git-sha>-<timestamp>.tar.gz
```

### config 发布

config 不建议和 bundle 混成一个 tar 包。原因是 config 更新频率更高，而且它的生命周期和安全边界都跟二进制不同。

如果要集中托管 config，建议上传的是“脱敏后的模板”，而不是本机原始文件：

```text
cua/configs/blackbox-runtime-template-<version>.json
```

模板里只能保留语义，不能保留：

- 明文 key。
- cookie / token。
- 本机绝对路径。
- 只对个人机器有意义的目录。

## TOS 获取与下载

服务节点拿 package 的优先级建议保持和 VM native 一致：

1. `--cua_package_url_refresh_cmd` / `OSWORLD_CUA_PACKAGE_URL_REFRESH_CMD`
2. `--cua_package_url` / `OSWORLD_CUA_PACKAGE_URL`
3. `--cua_package_tos_bucket` + `--cua_package_tos_key` + `tosutil presign`

config 如果也走 TOS，优先级建议单独配置，不要和 binary package 混写。

下载规则：

- 下载前先查本地 `current` 是否已经命中同一个 `sha256`。
- 未命中时下载到 cache。
- 下载后先校验 sha256，再解压。
- 解压必须进入临时目录，成功后再原子切换 `current`。
- 同一台节点多 worker 并发启动时，必须用本地锁避免重复解压。

## 服务节点目录布局

推荐布局：

```text
/home/user/.local/share/osworld-cua/
  current -> /home/user/.local/share/osworld-cua/releases/<package-version-or-sha>
  releases/
    <package-version-or-sha>/
      cua-linux-x64-pkg/
        cua-linux-x64.sh
        cua-linux-x64.cjs
        node_modules/

/home/user/.cache/osworld-cua-packages/
  <sha256>.tar.gz
  <sha256>.installed

/home/user/.config/osworld-cua/
  blackbox.json
  blackbox.redacted.json

/home/user/.local/share/osworld-cua-runs/
```

如果一台服务节点上同时跑多个 worker，这些 worker 可以共享同一份 `current` 和 cache，但不能共享未加锁的安装流程。

## 配置生成

黑盒 runner 的配置生成建议按这个顺序做：

1. 读取语义源 config。
2. 计算 source config sha256。
3. 将路径字段改成运行节点上的路径。
4. 将密钥字段改成环境变量占位符。
5. 落盘运行时 config。
6. 另存一份 redacted config，进入结果目录。

推荐保留的环境变量：

- `CUA_MODEL_API_KEY`
- `CUA_MODEL_BASE_URL`
- `CUA_MODEL_NAME`
- `CUA_RUNS_DIR`

建议保留的路径字段：

- `agent.runsDir`
- `agent.artifacts`
- `agent.records`
- `agent.knowledge`
- `coords.normalizedInput`

如果后续 CUA CLI 再补黑盒专用参数，优先在模板里改，不要把实验字段硬塞进 runner 主逻辑。

## 启动流程

服务节点上的黑盒启动顺序建议是：

```text
1. resolve package URL
2. install package to current/
3. load or fetch source config template
4. render runtime config
5. export CUA env vars
6. execute run_multienv_cua_blackbox.py
7. write meta / failure / result / artifact
```

这里的关键点是：下载、安装、渲染都发生在进入黑盒 runner 之前，runner 还是只吃本地路径。

## 元数据

建议在结果里记录这些字段：

- `cua_binary_path`
- `cua_binary_sha256`
- `cua_binary_source`
- `package_version`
- `package_sha256`
- `package_url_redacted`
- `source_config_path`
- `source_config_sha256`
- `runtime_config_path`
- `runtime_config_sha256`
- `runtime_config_redacted_path`
- `config_source_mode`

不要记录：

- 完整 presigned URL。
- TOS AK/SK。
- 原始 API key。
- 任何未脱敏的本机绝对路径。

## 失败分类

建议单独区分这些失败：

- `cua_package_url_missing`
- `cua_package_download_failed`
- `cua_package_checksum_mismatch`
- `cua_package_extract_failed`
- `cua_package_entrypoint_missing`
- `cua_config_source_missing`
- `cua_config_render_failed`
- `cua_config_invalid`
- `cua_dependency_missing`
- `cua_start_failed`

这些失败和 `cua_run_failed` 不是一回事。
前者说明运行时依赖没搭好，后者说明 CUA 已经起来了但任务执行失败。

## 和 VM native 的关系

blackbox 和 VM native 复用同一个 bundle 规则，但安装位置不同：

- blackbox：装在 runtime host 上，供 `run_multienv_cua_blackbox.py` 使用。
- vm_native：装在每台 VM 内，供 VM 内本地运行使用。

两者应该共享这些口径：

- `package_version`
- `package_sha256`
- `TOS object key`
- redacted config 规则
- 元数据字段命名

两者不应该共享这些实现细节：

- 安装 target path。
- 启动 wrapper。
- 运行时 `cwd`。

## 对外建议

如果后面要把 blackbox runner 也做成 Runtime Service，推荐让服务层做一层 bootstrap，负责：

- 拉包。
- 生成 config。
- 注入本地路径。
- 再调用现有 `run_multienv_cua_blackbox.py`。

这样 OSWorld 侧的 runner 主逻辑不需要知道 TOS，也不需要知道 secret 怎么发。
