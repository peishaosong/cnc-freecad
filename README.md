# CNC AutoCAM

> 基于 FreeCAD 的 CNC 自动编程模块（Workbench + 一键 G-code）

## 快速开始

**无需安装。** 克隆 + 启动：

```bash
git clone https://github.com/peishaosong/cnc-freecad.git
cd cnc-freecad
./scripts/start_freecad.sh
```

FreeCAD 启动后，下拉菜单选工作台 **"CNC AutoCAM"** 即可。

## 工具栏命令

| 快捷键 | 功能 |
|--------|------|
| Ctrl+I | 导入 STEP/IGES 零件 |
| Ctrl+F | 手动定义型腔特征 |
| Ctrl+T | 选刀具（预设库） |
| Ctrl+M | 选工艺模板 |
| Ctrl+G | 生成刀路（3D 视图显示） |
| Ctrl+E | 输出 G-code（保存 .nc） |

## 开发模式

代码改动保存后，在 FreeCAD 里执行 `Tools > Reload Scripts` 或重启即可生效，**无需重启整个应用**。

## 脚本入口

```bash
./scripts/run.sh verify        # M0 环境验证
./scripts/run.sh hello         # Hello CNC demo
./scripts/run.sh test          # M0 测试
./scripts/run.sh m1            # M1 core 测试
./scripts/run.sh ui            # M1 UI 测试
./scripts/run.sh all           # M0 + M1 core
./scripts/run.sh all-ui        # M0 + M1 core + UI
./scripts/run.sh cli info      # CLI: 版本信息
./scripts/run.sh cli run-pocket --width 80 --depth 80 --pocket-depth 15 -o pocket.nc
./scripts/run.sh start         # 启动 FreeCAD GUI
```

## 项目结构

```
cnc-freecad/
├── src/
│   └── cnc_freecad/
│       ├── core/              核心算法（刀路生成/后处理）
│       ├── data/              数据模型（Pydantic v2）
│       ├── freecad/           FreeCAD UI 集成
│       │   ├── workbench.py
│       │   ├── commands/      6 个 UI 命令
│       │   └── visualize.py   刀路 3D 显示
│       └── __main__.py        CLI 入口
├── tests/                     测试套
├── examples/                  示例 G-code
├── scripts/                   启动 + 工具脚本
└── docs/                      技术文档（外部：~/Desktop/松少/docs/cnc-freecad/）
```

## 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| FreeCAD | ≥ 1.0 | 平台/几何内核 |
| Python | ≥ 3.11 | FreeCAD 自带 |
| Pydantic | ≥ 2.0 | 数据模型（已在 FreeCAD Python 中） |
| NumPy | ≥ 1.26 | 路径计算 |

## 命令行工具

```bash
# 直接生成简单型腔 G-code（无需 FreeCAD GUI）
PYTHONPATH=src \
  /Applications/FreeCAD.app/Contents/Resources/bin/python \
  -m cnc_freecad run-pocket \
    --width 80 --depth 80 --pocket-depth 15 \
    --tool-diameter 12 \
    --output pocket.nc
```

## 完整文档

技术开发文档位于 `~/Desktop/松少/docs/cnc-freecad/`，共 8 份：
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
| M0 环境验证 | ✅ 完成 |
| M1 最小闭环 | ✅ 完成（含 FreeCAD UI） |
| M2 特征识别 | 📋 待开始 |
| M3 工艺匹配 | 📋 待开始 |

## 版本

v0.1.0 (M1)

---

*最后更新：2026-07-08*