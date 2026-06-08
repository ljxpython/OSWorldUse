# Scripts Directory

This directory contains all the run scripts for OSWorld, organized by type.

## Structure

```
scripts/
├── python/          # Python run scripts for various models
│   ├── run_*.py     # Individual model run scripts
│   └── run_multienv_*.py  # Multi-environment run scripts
└── bash/            # Bash scripts
    └── run_*.sh     # Shell scripts for running models
```

## Python Scripts

The `python/` directory contains Python scripts for running different models and agents:

- **Single model scripts**: `run_autoglm.py`, `run_coact.py`, `run_maestro.py`
- **Multi-environment scripts**: `run_multienv_*.py` - Scripts for running models in multiple environments
- **Manual examination**: `manual_examine.py` - Tool for manually verifying and examining specific benchmark tasks

## Bash Scripts

The `bash/` directory contains shell scripts for running specific models:

- `run_dart_gui.sh` - Run DART GUI model
- `run_os_symphony.sh` - Run OS Symphony model
- `run_manual_examine.sh` - Example script for manual task examination with sample task IDs

> **Note**: Due to previous oversight, many bash scripts were not preserved during the reorganization. We will gradually add more bash scripts in future updates. Community contributions are welcome! If you have bash scripts for running specific models or workflows, please feel free to submit a pull request.

## Usage

**Important**: All scripts should be run from the **project root directory** (not from within the scripts/ directory).

### Running Python Scripts

```bash
# From the OSWorld root directory
python scripts/python/run_multienv.py [args]

# Example: Run with OpenAI GPT-4o
python scripts/python/run_multienv.py \
    --provider_name docker \
    --headless \
    --observation_type screenshot \
    --model gpt-4o \
    --max_steps 15 \
    --num_envs 10 \
    --client_password password
```

### Running Bash Scripts

```bash
# From the OSWorld root directory
bash scripts/bash/run_dart_gui.sh [args]
```

### XUA OSWorld Runtime Local Service

`scripts/bash/xua_osworld_runtime_local.sh` is only responsible for the OSWorld
Runtime API service used by XUA-Eval local integration testing. It does not start
the XUA-Eval platform API or web console.

Run from the OSWorld repository root:

```bash
bash scripts/bash/xua_osworld_runtime_local.sh start
bash scripts/bash/xua_osworld_runtime_local.sh status
bash scripts/bash/xua_osworld_runtime_local.sh logs
bash scripts/bash/xua_osworld_runtime_local.sh stop
```

清空 Runtime 本地状态：

```bash
bash scripts/bash/xua_osworld_runtime_local.sh reset
```

`reset` 会先停止 Runtime，然后清理 `XUA_LOCAL_E2E_DIR` 下的 Runtime 状态库、
Runtime 结果目录、bootstrap 目录以及 Runtime 自己的日志和 pid 文件。它不会清理
XUA-Eval 平台侧的 SQLite、artifact storage 或 Web/API 日志。需要清整条本地链路
时，使用 XUA-Eval 侧控制脚本的 `reset`。

Default endpoint:

```text
http://127.0.0.1:7001/v1
```

Useful overrides:

```bash
export XUAEVAL_HOME="/Users/bytedance/PycharmProjects/work/xua-eval"
export XUA_LOCAL_E2E_DIR="/tmp/xua-osworld-e2e-local"
export OSWORLD_RUNTIME_PORT="7001"
```

For the full local chain, prefer the XUA-Eval side controller:

```bash
cd "/Users/bytedance/PycharmProjects/work/xua-eval"
bash scripts/local-osworld-e2e/local_osworld_e2e.sh start
```

### Manual Task Examination

For manual verification and examination of specific benchmark tasks:

```bash
# From the OSWorld root directory
python scripts/python/manual_examine.py \
    --headless \
    --observation_type screenshot \
    --result_dir ./results_human_examine \
    --test_all_meta_path evaluation_examples/test_all.json \
    --domain libreoffice_impress \
    --example_id a669ef01-ded5-4099-9ea9-25e99b569840 \
    --max_steps 3
```

This tool allows you to:
- Manually execute tasks in the environment
- Verify task correctness and evaluation metrics
- Record the execution process with screenshots and videos
- Examine specific problematic tasks

See `scripts/bash/run_manual_examine.sh` for example task IDs across different domains.

## Technical Details

All Python scripts in this directory have been configured with automatic path resolution to import modules from the project root. This means:

1. **You must run scripts from the project root directory**
2. Scripts automatically add the project root to `sys.path`
3. All imports (like `lib_run_single`, `desktop_env`, `mm_agents`) work correctly

## Adding New Scripts

If you create a new run script, make sure to include the following path setup at the beginning (after standard library imports but before project imports):

```python
# Add project root to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# Now you can import project modules
import lib_run_single
from desktop_env.desktop_env import DesktopEnv
from mm_agents.your_agent import YourAgent
```
