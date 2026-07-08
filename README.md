# CNC AutoCAM

> 基于 FreeCAD 的 CNC 自动编程模块

## 当前状态

🚧 **M0 — 环境验证** 进行中

## 项目结构

```
cnc-freecad/
├── docs/                     # 技术文档（外部：~/Desktop/松少/docs/cnc-freecad/）
├── src/
│   ├── cnc_freecad/          # 主模块
│   │   ├── core/             # 核心算法（特征识别/刀路生成/后处理/仿真）
│   │   ├── data/             # 数据模型（Feature/Tool/Material/ProcessTemplate）
│   │   └── freecad/          # FreeCAD 集成（Workbench/Commands/UI）
│   ├── postprocessors/       # 后处理器（Fanuc/三菱/海德汉）
│   └── process_templates/    # 工艺模板库（JSON）
├── tests/                    # 单元测试
├── examples/                 # 示例零件
└── scripts/                  # 工具脚本
```

## 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | ≥ 3.11 | FreeCAD 1.x 自带 Python 3.11 |
| FreeCAD | ≥ 1.0 | 平台/几何内核 |
| Pydantic | ≥ 2.0 | 数据模型验证（可选） |

## 安装

### macOS（已验证）

```bash
# FreeCAD 已安装（/Applications/FreeCAD.app）
# 使用 FreeCAD 自带的 Python
FREECAD_PYTHON=/Applications/FreeCAD.app/Contents/Resources/bin/python

# 创建虚拟环境
uv venv .venv --python $FREECAD_PYTHON

# 安装项目依赖（开发模式）
.venv/bin/pip install -e ".[dev]"
```

## 运行

```bash
# 验证环境
freecadcmd -c "import sys; sys.path.insert(0, 'src'); import cnc_freecad; print(cnc_freecad.__version__)"

# 运行测试
freecadcmd -c "import sys; sys.path.insert(0, 'src'); import pytest; pytest.main(['tests/', '-v'])"
```

## 文档

完整技术开发文档： [~/Desktop/松少/docs/cnc-freecad/](../docs/cnc-freecad/)

## 版本

- v0.1.0 — M0 环境验证（当前）

---

*最后更新：2026-07-08*