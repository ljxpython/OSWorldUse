# Evaluation Case Analysis
这个目录专门汇总 `evaluation_examples/` 里的评测 case。老王先把边界钉死：`examples/`、`examples_windows/`、`cua_blackbox/cases/` 是 case 本体；`test_*.json` 和 `cua_blackbox/suites/*.json` 是任务索引或套件配置；`settings/` 是账号、代理、应用配置，不算 case 本体。

## 文档入口
- [Linux/Ubuntu case 清单](./linux-cases.md)
- [Windows case 清单](./windows-cases.md)
- [CUA blackbox case 清单](./cua-blackbox-cases.md)
- [评测标准体系与准确性保证](./evaluation-methodology.md)
- [逐 case 详细分析](./details/README.md)
- [索引与配置文件说明](./suites-and-support-files.md)

## 总量
| 范围 | case 数 | 源目录 |
| --- | ---: | --- |
| Linux/Ubuntu 主任务集 | 369 | `evaluation_examples/examples/` |
| Windows 任务集 | 49 | `evaluation_examples/examples_windows/` |
| CUA blackbox 自定义任务集 | 1 | `evaluation_examples/cua_blackbox/cases/` |
| 合计 | 419 | - |

## 应用域分布
| 范围 | 应用域 | case 数 |
| --- | --- | ---: |
| Linux/Ubuntu 主任务集 | `chrome` | 46 |
| Linux/Ubuntu 主任务集 | `gimp` | 26 |
| Linux/Ubuntu 主任务集 | `libreoffice_calc` | 47 |
| Linux/Ubuntu 主任务集 | `libreoffice_impress` | 47 |
| Linux/Ubuntu 主任务集 | `libreoffice_writer` | 23 |
| Linux/Ubuntu 主任务集 | `multi_apps` | 101 |
| Linux/Ubuntu 主任务集 | `os` | 24 |
| Linux/Ubuntu 主任务集 | `thunderbird` | 15 |
| Linux/Ubuntu 主任务集 | `vlc` | 17 |
| Linux/Ubuntu 主任务集 | `vs_code` | 23 |
| Windows 任务集 | `excel` | 11 |
| Windows 任务集 | `multi_app` | 22 |
| Windows 任务集 | `ppt` | 7 |
| Windows 任务集 | `word` | 9 |
| CUA blackbox 自定义任务集 | `chrome` | 1 |

## 怎么读这些 case
- `instruction` 是 agent 真正要完成的用户目标，下面清单的“任务”直接保留这个字段，避免二次改写把评测意图带歪。
- `config` 是 reset 时会执行的前置动作，比如下载文件、启动应用、打开文档、执行脚本。
- `evaluator.func` 是成功判定方式，常见模式包括文件对比、表格对比、URL/标签页检查、截图结构相似度、配置项检查和 `infeasible`。
- `related_apps` 能快速判断单应用还是多应用任务，`multi_apps` 这种目录一般同时考察跨应用信息搬运和文件产物。

## 应用域粗分类
| 应用域 | 主要在评什么 |
| --- | --- |
| `chrome` | 浏览器设置、标签页/URL、书签、搜索、扩展、网页交互、账号/下载相关流程。 |
| `gimp` | 图片编辑、裁剪缩放、颜色/亮度/饱和度、图层或几何变化，主要靠图片相似度或文件属性评测。 |
| `libreoffice_calc / excel` | 电子表格清洗、公式、排序筛选、透视表、图表、格式和导出结果。 |
| `libreoffice_impress / ppt` | 演示文稿页面、布局、主题、颜色、转场、导出 PDF/PPTX 等产物。 |
| `libreoffice_writer / word` | 文档排版、页眉页脚、字体、表格、引用、分页、导出 PDF/DOCX。 |
| `multi_apps / multi_app` | 跨应用工作流，比如邮件到表格、浏览器到办公文档、文件压缩/导出/转换。 |
| `os` | 桌面系统和文件管理任务，也包含明确不可行任务。 |
| `thunderbird` | 邮件客户端设置、过滤器、文件夹、偏好、附件或邮件内容检查。 |
| `vlc` | 播放器设置、播放状态、音量、录制、媒体文件输出和元数据。 |
| `vs_code` | 编辑器设置、快捷键、扩展、代码文件修改和测试套件校验。 |
| `cua_blackbox/cases` | 给 blackbox bridge 的最小自定义回归 case，目前只有 Chrome 下载页导航样例。 |

## 维护规则
- 新增 case 后，优先更新对应平台清单，至少写清 `id`、源 JSON、任务、前置动作、评测函数。
- 如果只是新增 suite/index，不要混进 case 清单，放到索引与配置说明里。
- 如果 `instruction` 太长，宁可保留原文，也别擅自总结成看似聪明实则漏条件的垃圾。
