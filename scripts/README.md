Format JSON helper

- `scripts/format_json.py`：简单脚本，用于将指定 JSON 文件原地格式化。

示例：

```bash
python scripts/format_json.py llm_prompts/test1.json
```

在 VS Code 中：

- 推荐安装 `esbenp.prettier-vscode`，并在工作区启用 `editor.formatOnSave`。
- 本仓库已添加 `.vscode/extensions.json` 与 `.vscode/settings.json`。
