# CNC AutoCAM

> 基于 FreeCAD 的 CNC 自动编程模块（Workbench + 一键 G-code）

## 快速开始

**两步**：

```bash
git clone https://github.com/peishaosong/cnc-freecad.git
cd cnc-freecad
./scripts/setup.sh           # 一次性安装
open /Applications/FreeCAD.app
```

下拉工作台菜单选 **"CNC AutoCAM"**。

之后任何方式启动 FreeCAD（Dock / Spotlight / 命令行 / 双击 .app），CNC AutoCAM 都自动出现。

## 工具栏命令

| 快捷键 | 功能 |
|--------|------|
| Ctrl+I | 导入 STEP/IGES 零件 |
| Ctrl+F | 手动定义型腔特征 |
| Ctrl+T | 选刀具（预设库） |
| Ctrl+M | 选工艺模板 |
| Ctrl+G | 生成刀路（3D 视图显示） |
| Ctrl+E | 输出 G-code（保存 .nc） |

## 卸载

```bash
./scripts/setup.sh remove
```

## 开发模式

代码改了保存后，在 FreeCAD 里：
- `Tools > Reload Scripts`，或
- 重启 FreeCAD

无需重新 setup。

## 脚本入口

```bash
./scripts/setup.sh            # 一次性安装（创建符号链接到 ~/.FreeCAD/Mod/）
./scripts/setup.sh status     # 查看安装状态
./scripts/setup.sh remove     # 卸载

./scripts/run.sh verify       # M0 环境验证
./scripts/run.sh hello        # Hello CNC demo
./scripts/run.sh test         # M0 测试
./scripts/run.sh m1           # M1 core 测试
./scripts/run.sh ui           # M1 UI 测试
./scripts/run.sh all          # M0 + M1 core
./scripts/run.sh all-ui       # M0 + M1 core + UI
./scripts/run.sh cli info     # CLI: 版本信息
./scripts/run.sh cli run-pocket --width 80 --depth 80 -o pocket.nc
```

## 项目结构

```
cnc-freecad/
├── src/
│   ├── cnc_freecad/          # Python package
│   │   ├── core/             核心算法（刀路生成/后处理）
│   │   ├── data/             数据模型（Pydantic v2）
│   │   ├── freecad/          FreeCAD UI 集成
│   │   │   ├── workbench.py
│   │   │   ├── commands/     6 个 UI 命令
│   │   │   └── visualize.py  刀路 3D 显示
│   │   └── __main__.py       CLI 入口
│   └── Mod/
│       └── CncmAutoCAM/
│           └── InitGui.py    # FreeCAD 自动加载入口
├── tests/                    测试套
├── examples/                 示例 G-code
├── scripts/                  setup.sh / run.sh / 测试脚本
└── docs/                     技术文档（外部：~/Desktop/松少/docs/cnc-freecad/）
```

## 环境要求

| 依赖 | 版本 |
|------|------|
| FreeCAD | ≥ 1.0 |
| Python | ≥ 3.11 (FreeCAD 自带) |
| Pydantic | ≥ 2.0 (FreeCAD 自带) |
| NumPy | ≥ 1.26 (FreeCAD 自带) |

## 工作原理

`./scripts/setup.sh` 在用户级 FreeCAD Mod 目录创建符号链接：

```
~/Library/Application Support/FreeCAD/v1-1/Mod/CncmAutoCAM
    → /Users/<you>/path/to/cnc-freecad/src/Mod/CncmAutoCAM
```

FreeCAD 启动时扫描这个目录，执行 `InitGui.py`，加载项目代码并注册 workbench。修改项目代码后重启 FreeCAD 生效，无需重新 setup。

## 完整文档

`~/Desktop/松少/docs/cnc-freecad/` 共 8 份：
- `00-overview.md` — 项目背景/目标
- `01-architecture.md` — 系统架构
- `02-tech-stack.md` — 技术选型
- `03-data-model.md` — 数据模型
- `04-api-spec.md` — API 规范
- `05-core-flow.md` — 核心流程
- `06-milestones.md` — 里程碑计划
- `07-tech-debt.md` — 已知限制

## 当前状态

| 阶段 | 状态 |
|------|------|
| M0 环境验证 | ✅ |
| M1 最小闭环（含 FreeCAD UI） | ✅ |
| M2 特征识别 | 📋 待开始 |

## 版本

v0.1.0 (M1)

---

*最后更新：2026-07-08*