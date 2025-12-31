# Agent Skills 总纲（本仓库）

## Skills 是什么

Skills 是一组可复用的“任务能力包”，用于把通用 Agent 快速变成某个领域/流程的专用 Agent。一个 skill 通常包含：

- `SKILL.md`：该 skill 的元数据（触发描述）与使用说明
- `scripts/`：可直接运行的脚本（优先当作黑盒工具调用）
- `references/`：按需查阅的参考资料（避免把大段资料塞进 `SKILL.md`）
- `assets/`：模板/素材等（通常不需要读入上下文）

## 去哪里找 Skills

本仓库的技能目录在：

- `skills/`

每个子目录就是一个 skill，例如：

- `skills/<skill-name>/SKILL.md`

## 如何使用 Skills

### 1) 先定位合适的 skill

按任务关键词在 `skills/` 里浏览，重点看每个 skill 的 `SKILL.md` 的 YAML `description`（它决定何时触发/何时该用这个 skill）。

### 2) 按 SKILL.md 的指引使用脚本

大多数技能会在 `scripts/` 下提供可执行脚本。

实践原则：

1. 先运行 `--help` 查看参数与示例
2. 优先直接调用脚本完成任务（把脚本当黑盒），除非确实需要改功能

### 3) 需要更深细节时再读 references

当 SKILL.md 提示“阅读 references/xxx.md”时再去加载该文件；避免一次性加载大文档。

## 常见用法模板

```bash
# 进入 skill 目录（如 SKILL.md 建议）
cd skills/<skill-name>

# 先看帮助
python scripts/<tool>.py --help

# 再按 SKILL.md 示例调用
python scripts/<tool>.py <subcommand> [args...]
```
