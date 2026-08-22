# WorkBuddy Skills 仓库

跨设备同步用户级 Skill，排除 node_modules 等不可移植文件。

## 本仓库包含

| Skill | 大小 | 依赖 |
|-------|------|------|
| gzh-design-skill | ~7MB | 需要 `pnpm install` |
| gzh-general-publish | 148K | 无 |
| gzh-lawyer-publish | 2.3M | 无 |
| tencent-cos-uploader | 16K | 无 |
| ur-report-rigor | 8K | 无 |
| ur-data-analysis | 8K | 无 |
| game-ur-report | 8K | 无（建议与 ur-report-rigor 联用） |
| wechat-article-pro | 8K | 无 |
| wechat-publisher | 48K | 无 |

## 在另一台设备安装

```bash
# 1. 克隆仓库
cd ~/.workbuddy
mv skills skills.bak  # 备份原有目录（如果存在）
git clone https://github.com/jkfaf/workbuddy-skills.git skills

# 2. 安装 gzh-design-skill 依赖
cd skills/gzh-design-skill/assets/doocs-md
pnpm install

# 3. 重启 WorkBuddy，自动识别新 skill
```

## 日常同步

```bash
# 设备 A 改了 skill 后推送
cd ~/.workbuddy/skills
git add -A && git commit -m "update skills" && git push

# 设备 B 拉取
cd ~/.workbuddy/skills
git pull
```

## 注意事项

- `node_modules/`、`.pnpm/`、`*.zip` 已在 .gitignore 中排除
- gzh-design-skill 的 doocs-md 是第三方项目，改了之后用 `pnpm install` 重装依赖
- 同步后需重启 WorkBuddy 才能生效
- 元数据文件 `.disable_to_model_invocation_migration.json` 和 `_bm_skillid_migration.json` 也已纳入版本控制
