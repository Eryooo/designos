"""Frontend Codegen — MOCK implementation.

⚠️ STATUS: Mock. All four core functions return fixed example data so
prd2proto pipeline can be wired end-to-end before the real implementation
ships in P3.

Real implementation in P3 must replace the bodies of these functions
WITHOUT changing the schemas in `schemas.py`. Pipeline stages and tests
will keep working unchanged.

Functions:
    fetch_dsl       — Returns a hand-written DSL tree (Figma- or MasterGo-shaped).
    extract_tokens  — Returns a sane default token set.
    map_components  — Returns a mapping with 100% mock coverage.
    generate_code   — Writes a minimal placeholder React project to disk.
"""

from __future__ import annotations

from pathlib import Path

from schemas import (
    ComponentMapping,
    DesignTokens,
    DSLFetchRequest,
    DSLFetchResponse,
    DSLNode,
    ExtractTokensRequest,
    ExtractTokensResponse,
    GenerateCodeRequest,
    GenerateCodeResponse,
    MapComponentsRequest,
    MapComponentsResponse,
)


class FrontendCodegenError(Exception):
    """Base exception for frontend-codegen errors."""


# ---------------------------------------------------------------------------
# Mock fixtures
# ---------------------------------------------------------------------------


def _mock_dsl_tree() -> DSLNode:
    """A small but realistic DSL tree: a login screen with two inputs + a button."""
    return DSLNode(
        id="frame-root",
        type="Frame",
        name="LoginScreen",
        properties={"width": 375, "height": 812, "fill": "#FFFFFF"},
        children=[
            DSLNode(
                id="text-title",
                type="Text",
                name="Title",
                properties={
                    "fontSize": 24,
                    "fontWeight": 600,
                    "color": "#1F2937",
                    "content": "登录",
                },
            ),
            DSLNode(
                id="input-username",
                type="Input",
                name="UsernameInput",
                properties={
                    "placeholder": "用户名",
                    "padding": 12,
                    "borderRadius": 8,
                    "borderColor": "#D1D5DB",
                },
            ),
            DSLNode(
                id="input-password",
                type="Input",
                name="PasswordInput",
                properties={
                    "placeholder": "密码",
                    "type": "password",
                    "padding": 12,
                    "borderRadius": 8,
                    "borderColor": "#D1D5DB",
                },
            ),
            DSLNode(
                id="button-submit",
                type="Button",
                name="SubmitButton",
                properties={
                    "label": "登录",
                    "fill": "#3B82F6",
                    "color": "#FFFFFF",
                    "padding": 14,
                    "borderRadius": 8,
                },
            ),
        ],
    )


def _mock_tokens() -> DesignTokens:
    """A small but realistic token set."""
    return DesignTokens(
        colors={
            "color.text.primary": "#1F2937",
            "color.text.secondary": "#6B7280",
            "color.surface.background": "#FFFFFF",
            "color.surface.border": "#D1D5DB",
            "color.brand.primary": "#3B82F6",
            "color.brand.primary.hover": "#2563EB",
            "color.feedback.error": "#EF4444",
        },
        typography={
            "title.lg": {"fontSize": 24, "fontWeight": 600, "lineHeight": "32px"},
            "body.md": {"fontSize": 14, "fontWeight": 400, "lineHeight": "20px"},
        },
        spacing={
            "spacing.xs": "4px",
            "spacing.sm": "8px",
            "spacing.md": "12px",
            "spacing.lg": "16px",
        },
        radius={
            "radius.sm": "4px",
            "radius.md": "8px",
        },
        shadow={
            "shadow.sm": "0 1px 2px rgba(0,0,0,0.05)",
        },
    )


# ---------------------------------------------------------------------------
# Public API (stable across mock + real implementation)
# ---------------------------------------------------------------------------


def fetch_dsl(req: DSLFetchRequest) -> DSLFetchResponse:
    """Fetch DSL from Figma or MasterGo.

    MOCK: returns a hand-written login-screen DSL regardless of source/file_id.
    Real impl: hits Figma/MasterGo SDK or local mcp servers.
    """
    return DSLFetchResponse(
        source=req.source,
        file_id=req.file_id,
        root=_mock_dsl_tree(),
        is_mock=True,
    )


def extract_tokens(req: ExtractTokensRequest) -> ExtractTokensResponse:
    """Extract Design Tokens from DSL + design.md.

    MOCK: returns a fixed token set regardless of input.
    Real impl: scans DSL tree leaves + parses design.md to fuse tokens.
    """
    _ = req  # Mock ignores input
    return ExtractTokensResponse(tokens=_mock_tokens(), is_mock=True)


def map_components(req: MapComponentsRequest) -> MapComponentsResponse:
    """Map DSL nodes to component-library components.

    MOCK: applies a tiny hand-written mapping table.
    Real impl: classifier (rule + LLM judge) per node.
    """
    # Naive: walk the DSL tree, map by node.type to a component-lib name.
    type_map_per_lib: dict[str, dict[str, str]] = {
        "antd-vue": {
            "Input": "AInput",
            "Button": "AButton",
            "Text": "ATypography.Text",
            "Frame": "div",
        },
        "antd-react": {
            "Input": "Input",
            "Button": "Button",
            "Text": "Typography.Text",
            "Frame": "div",
        },
        "element-plus": {
            "Input": "ElInput",
            "Button": "ElButton",
            "Text": "span",
            "Frame": "div",
        },
        "custom": {
            "Input": "Input",
            "Button": "Button",
            "Text": "Text",
            "Frame": "div",
        },
    }
    type_map: dict[str, str] = type_map_per_lib.get(req.component_lib, {})

    mappings: dict[str, str] = {}
    unmapped: list[str] = []

    def walk(node: DSLNode) -> None:
        comp = type_map.get(node.type)
        if comp is None:
            unmapped.append(node.id)
        else:
            mappings[node.id] = comp
        for child in node.children:
            walk(child)

    walk(req.dsl.root)
    total = len(mappings) + len(unmapped)
    coverage = (len(mappings) / total) if total > 0 else 1.0
    return MapComponentsResponse(
        mapping=ComponentMapping(
            mappings=mappings,
            unmapped_node_ids=unmapped,
            coverage_rate=coverage,
        ),
        is_mock=True,
    )


def generate_code(req: GenerateCodeRequest) -> GenerateCodeResponse:
    """Generate frontend project at output_dir.

    MOCK: writes a minimal React project skeleton (package.json + App.jsx + index.html)
    based on mode. Real impl: full DSL → component tree → state coverage codegen.
    """
    output_dir = Path(req.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    if req.framework == "react":
        files = _write_react_skeleton(output_dir, mode=req.mode)
    elif req.framework == "vue":
        files = _write_vue_skeleton(output_dir, mode=req.mode)
    else:
        raise FrontendCodegenError(f"unsupported framework: {req.framework}")

    return GenerateCodeResponse(
        output_dir=str(output_dir),
        files_written=files,
        framework=req.framework,
        mode=req.mode,
        is_mock=True,
        next_steps=[
            f"cd {output_dir}",
            "npm install",
            "npm run dev",
        ],
    )


def _write_react_skeleton(out: Path, *, mode: str) -> list[str]:
    files: list[str] = []

    package_json = """{
  "name": "prd2proto-mock",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
"""
    (out / "package.json").write_text(package_json, encoding="utf-8")
    files.append("package.json")

    index_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>prd2proto mock</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
"""
    (out / "index.html").write_text(index_html, encoding="utf-8")
    files.append("index.html")

    src_dir = out / "src"
    src_dir.mkdir(exist_ok=True)

    main_jsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
"""
    (src_dir / "main.jsx").write_text(main_jsx, encoding="utf-8")
    files.append("src/main.jsx")

    app_jsx = f"""import React, {{ useState }} from 'react';

// Generated by frontend-codegen MOCK (mode={mode})
// Replace with real DSL-driven output when P3 ships.
export default function App() {{
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  return (
    <div style={{{{ padding: 24, fontFamily: 'system-ui, sans-serif' }}}}>
      <h1>登录</h1>
      <input
        value={{user}}
        onChange={{(e) => setUser(e.target.value)}}
        placeholder="用户名"
        style={{{{ display: 'block', padding: 12, marginBottom: 12, width: 240 }}}}
      />
      <input
        type="password"
        value={{pass}}
        onChange={{(e) => setPass(e.target.value)}}
        placeholder="密码"
        style={{{{ display: 'block', padding: 12, marginBottom: 12, width: 240 }}}}
      />
      <button style={{{{ padding: '12px 24px', background: '#3B82F6', color: '#FFF', border: 0 }}}}>
        登录
      </button>
    </div>
  );
}}
"""
    (src_dir / "App.jsx").write_text(app_jsx, encoding="utf-8")
    files.append("src/App.jsx")

    readme = f"""# prd2proto MOCK output

This project was produced by `mcp-servers/frontend-codegen` in MOCK mode
({mode} fidelity tier). It compiles and runs but the layout is hand-written —
real DSL-driven generation arrives with frontend-codegen P3.

```
npm install
npm run dev
```
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    files.append("README.md")

    return files


def _write_vue_skeleton(out: Path, *, mode: str) -> list[str]:
    files: list[str] = []

    package_json = """{
  "name": "prd2proto-mock",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "vue": "^3.4.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^5.0.0"
  }
}
"""
    (out / "package.json").write_text(package_json, encoding="utf-8")
    files.append("package.json")

    index_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>prd2proto mock</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
"""
    (out / "index.html").write_text(index_html, encoding="utf-8")
    files.append("index.html")

    src_dir = out / "src"
    src_dir.mkdir(exist_ok=True)

    main_js = """import { createApp } from 'vue';
import App from './App.vue';
createApp(App).mount('#app');
"""
    (src_dir / "main.js").write_text(main_js, encoding="utf-8")
    files.append("src/main.js")

    app_vue = f"""<!-- Generated by frontend-codegen MOCK (mode={mode}) -->
<script setup>
import {{ ref }} from 'vue';
const user = ref('');
const pass = ref('');
</script>

<template>
  <div :style="{{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}">
    <h1>登录</h1>
    <input v-model="user" placeholder="用户名" />
    <input v-model="pass" type="password" placeholder="密码" />
    <button>登录</button>
  </div>
</template>
"""
    (src_dir / "App.vue").write_text(app_vue, encoding="utf-8")
    files.append("src/App.vue")

    return files


__all__ = [
    "FrontendCodegenError",
    "extract_tokens",
    "fetch_dsl",
    "generate_code",
    "map_components",
]
