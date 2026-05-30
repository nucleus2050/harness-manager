from __future__ import annotations


_THEME_TOKENS = {
    "light": {
        "app_bg": "#eef2f7",
        "text": "#111827",
        "main_bg": "#eef2f7",
        "transparent": "transparent",
        "shell_bg": "#eef2f7",
        "titlebar_bg": "#ffffff",
        "titlebar_border": "#dbe3ef",
        "titlebar_text": "#334155",
        "titlebar_icon_bg": "#eaf1ff",
        "titlebar_button_hover": "#eaf1ff",
        "titlebar_close_hover": "#dc2626",
        "title": "#0f172a",
        "muted": "#64748b",
        "sidebar": "#0f172a",
        "sidebar_text": "#f8fafc",
        "sidebar_muted": "#94a3b8",
        "card": "#ffffff",
        "card_border": "#dbe3ef",
        "hero_start": "#ffffff",
        "hero_end": "#e8f0ff",
        "hero_border": "#d9e5fb",
        "sidebar_card": "#172554",
        "sidebar_card_border": "#1e3a8a",
        "pill_bg": "#111c35",
        "pill_border": "#263a63",
        "soft_card": "#f8fafc",
        "soft_border": "#e2e8f0",
        "client_border": "#dbeafe",
        "ready_bg": "#ecfdf5",
        "ready_border": "#86efac",
        "selected_bg": "#dbeafe",
        "selected_border": "#60a5fa",
        "client_path": "#475569",
        "ready_text": "#15803d",
        "missing_text": "#b45309",
        "list_text": "#172033",
        "hover_bg": "#eff6ff",
        "hover_border": "#bfdbfe",
        "primary": "#2563eb",
        "primary_hover": "#1d4ed8",
        "secondary_bg": "#eaf1ff",
        "button_bg": "#ffffff",
        "button_border": "#d0d8e6",
        "button_text": "#1f2937",
        "compact_border": "#cbd5e1",
        "compact_text": "#334155",
        "danger_bg": "#fff7f7",
        "danger_hover": "#fee2e2",
        "danger_border": "#fecaca",
        "danger_text": "#b91c1c",
        "scroll": "#cbd5e1",
    },
    "dark": {
        "app_bg": "#020617",
        "text": "#e5e7eb",
        "main_bg": "#020617",
        "transparent": "transparent",
        "shell_bg": "#020617",
        "titlebar_bg": "#111827",
        "titlebar_border": "#334155",
        "titlebar_text": "#e5e7eb",
        "titlebar_icon_bg": "#172554",
        "titlebar_button_hover": "#1e293b",
        "titlebar_close_hover": "#dc2626",
        "title": "#f8fafc",
        "muted": "#94a3b8",
        "sidebar": "#0f172a",
        "sidebar_text": "#f8fafc",
        "sidebar_muted": "#94a3b8",
        "card": "#111827",
        "card_border": "#334155",
        "hero_start": "#111827",
        "hero_end": "#172554",
        "hero_border": "#1e3a8a",
        "sidebar_card": "#172554",
        "sidebar_card_border": "#1e3a8a",
        "pill_bg": "#111c35",
        "pill_border": "#263a63",
        "soft_card": "#1e293b",
        "soft_border": "#334155",
        "client_border": "#334155",
        "ready_bg": "#052e1a",
        "ready_border": "#166534",
        "selected_bg": "#1e3a8a",
        "selected_border": "#60a5fa",
        "client_path": "#cbd5e1",
        "ready_text": "#86efac",
        "missing_text": "#fbbf24",
        "list_text": "#e5e7eb",
        "hover_bg": "#1e3a8a",
        "hover_border": "#3b82f6",
        "primary": "#2563eb",
        "primary_hover": "#3b82f6",
        "secondary_bg": "#172554",
        "button_bg": "#1e293b",
        "button_border": "#475569",
        "button_text": "#e5e7eb",
        "compact_border": "#475569",
        "compact_text": "#e2e8f0",
        "danger_bg": "#450a0a",
        "danger_hover": "#7f1d1d",
        "danger_border": "#991b1b",
        "danger_text": "#fecaca",
        "scroll": "#475569",
    },
}

_THEME_TOKENS.update(
    {
        "obsidian": {
            **_THEME_TOKENS["dark"],
            "app_bg": "#000000",
            "text": "#e7e5e4",
            "main_bg": "#000000",
            "shell_bg": "#000000",
            "titlebar_bg": "#050505",
            "titlebar_border": "#27272a",
            "titlebar_text": "#fafaf9",
            "titlebar_icon_bg": "#111111",
            "titlebar_button_hover": "#18181b",
            "title": "#fafaf9",
            "muted": "#a8a29e",
            "sidebar": "#050505",
            "sidebar_card": "#0a0a0a",
            "sidebar_card_border": "#27272a",
            "card": "#050505",
            "card_border": "#27272a",
            "hero_start": "#050505",
            "hero_end": "#111111",
            "hero_border": "#27272a",
            "pill_bg": "#0a0a0a",
            "pill_border": "#27272a",
            "soft_card": "#0a0a0a",
            "soft_border": "#27272a",
            "client_border": "#3f3f46",
            "selected_bg": "#18181b",
            "selected_border": "#f5f5f4",
            "client_path": "#d6d3d1",
            "list_text": "#f5f5f4",
            "hover_bg": "#18181b",
            "hover_border": "#52525b",
            "primary": "#27272a",
            "primary_hover": "#3f3f46",
            "secondary_bg": "#111111",
            "button_bg": "#111111",
            "button_border": "#3f3f46",
            "button_text": "#fafaf9",
            "compact_border": "#3f3f46",
            "compact_text": "#e7e5e4",
            "scroll": "#52525b",
        },
        "matrix": {
            **_THEME_TOKENS["dark"],
            "app_bg": "#020403",
            "shell_bg": "#020403",
            "titlebar_bg": "#03110b",
            "titlebar_border": "#064e3b",
            "titlebar_text": "#bbf7d0",
            "titlebar_icon_bg": "#052e1a",
            "titlebar_button_hover": "#064e3b",
            "title": "#ecfdf5",
            "muted": "#86efac",
            "card": "#03110b",
            "card_border": "#065f46",
            "hero_start": "#03110b",
            "hero_end": "#052e1a",
            "hero_border": "#047857",
            "sidebar_card": "#04130c",
            "sidebar_card_border": "#047857",
            "soft_card": "#04130c",
            "soft_border": "#065f46",
            "client_border": "#047857",
            "selected_bg": "#064e3b",
            "selected_border": "#00ff88",
            "client_path": "#bbf7d0",
            "ready_text": "#00ff88",
            "list_text": "#dcfce7",
            "hover_bg": "#052e1a",
            "hover_border": "#00ff88",
            "primary": "#00ff88",
            "primary_hover": "#22c55e",
            "secondary_bg": "#052e1a",
            "button_bg": "#04130c",
            "button_border": "#047857",
            "button_text": "#dcfce7",
            "compact_border": "#047857",
            "compact_text": "#bbf7d0",
            "scroll": "#047857",
        },
        "neon": {
            **_THEME_TOKENS["dark"],
            "app_bg": "#0b0614",
            "shell_bg": "#0b0614",
            "titlebar_bg": "#160b2e",
            "titlebar_border": "#7c3aed",
            "title": "#fff7ff",
            "muted": "#f0abfc",
            "card": "#160b2e",
            "card_border": "#7c3aed",
            "hero_start": "#160b2e",
            "hero_end": "#3b0764",
            "hero_border": "#ff2bd6",
            "sidebar_card": "#1e103d",
            "sidebar_card_border": "#ff2bd6",
            "soft_card": "#1e103d",
            "soft_border": "#7c3aed",
            "selected_bg": "#581c87",
            "selected_border": "#ff2bd6",
            "primary": "#ff2bd6",
            "primary_hover": "#c026d3",
            "hover_bg": "#3b0764",
            "hover_border": "#ff2bd6",
            "compact_text": "#f5d0fe",
            "button_border": "#7c3aed",
            "scroll": "#a21caf",
        },
        "sunset": {
            **_THEME_TOKENS["light"],
            "app_bg": "#fff7ed",
            "shell_bg": "#fff7ed",
            "titlebar_bg": "#ffedd5",
            "titlebar_border": "#fed7aa",
            "title": "#431407",
            "muted": "#9a3412",
            "card": "#fffaf3",
            "card_border": "#fed7aa",
            "hero_start": "#fff7ed",
            "hero_end": "#fed7aa",
            "hero_border": "#fdba74",
            "sidebar": "#431407",
            "sidebar_card": "#7c2d12",
            "sidebar_card_border": "#fb923c",
            "soft_card": "#ffedd5",
            "soft_border": "#fdba74",
            "selected_bg": "#fed7aa",
            "selected_border": "#f97316",
            "primary": "#f97316",
            "primary_hover": "#ea580c",
            "hover_bg": "#ffedd5",
            "hover_border": "#fb923c",
            "compact_text": "#7c2d12",
            "scroll": "#fb923c",
        },
        "forest": {
            **_THEME_TOKENS["light"],
            "app_bg": "#f0fdf4",
            "shell_bg": "#f0fdf4",
            "titlebar_bg": "#dcfce7",
            "titlebar_border": "#bbf7d0",
            "title": "#052e16",
            "muted": "#166534",
            "card": "#f7fee7",
            "card_border": "#bbf7d0",
            "hero_start": "#f0fdf4",
            "hero_end": "#dcfce7",
            "hero_border": "#86efac",
            "sidebar": "#052e16",
            "sidebar_card": "#14532d",
            "sidebar_card_border": "#22c55e",
            "soft_card": "#dcfce7",
            "soft_border": "#86efac",
            "selected_bg": "#bbf7d0",
            "selected_border": "#22c55e",
            "primary": "#22c55e",
            "primary_hover": "#16a34a",
            "hover_bg": "#dcfce7",
            "hover_border": "#4ade80",
            "compact_text": "#14532d",
            "scroll": "#4ade80",
        },
        "aurora": {
            **_THEME_TOKENS["dark"],
            "app_bg": "#020617",
            "shell_bg": "#020617",
            "titlebar_bg": "#071426",
            "titlebar_border": "#155e75",
            "title": "#ecfeff",
            "muted": "#a5f3fc",
            "card": "#071426",
            "card_border": "#155e75",
            "hero_start": "#071426",
            "hero_end": "#0f766e",
            "hero_border": "#38bdf8",
            "sidebar_card": "#082f49",
            "sidebar_card_border": "#38bdf8",
            "soft_card": "#082f49",
            "soft_border": "#155e75",
            "selected_bg": "#164e63",
            "selected_border": "#38bdf8",
            "primary": "#38bdf8",
            "primary_hover": "#0891b2",
            "hover_bg": "#0e7490",
            "hover_border": "#38bdf8",
            "compact_text": "#cffafe",
            "scroll": "#38bdf8",
        },
        "ember": {
            **_THEME_TOKENS["dark"],
            "app_bg": "#120606",
            "shell_bg": "#120606",
            "titlebar_bg": "#1c0a0a",
            "titlebar_border": "#7f1d1d",
            "title": "#fff7ed",
            "muted": "#fed7aa",
            "card": "#1c0a0a",
            "card_border": "#7f1d1d",
            "hero_start": "#1c0a0a",
            "hero_end": "#431407",
            "hero_border": "#ef4444",
            "sidebar_card": "#270b0b",
            "sidebar_card_border": "#ef4444",
            "soft_card": "#270b0b",
            "soft_border": "#7f1d1d",
            "selected_bg": "#7f1d1d",
            "selected_border": "#ef4444",
            "primary": "#ef4444",
            "primary_hover": "#dc2626",
            "hover_bg": "#431407",
            "hover_border": "#ef4444",
            "compact_text": "#fed7aa",
            "scroll": "#ef4444",
        },
        "porcelain": {
            **_THEME_TOKENS["light"],
            "app_bg": "#f8fafc",
            "shell_bg": "#f8fafc",
            "titlebar_bg": "#ffffff",
            "titlebar_border": "#ccfbf1",
            "title": "#0f172a",
            "muted": "#475569",
            "card": "#ffffff",
            "card_border": "#ccfbf1",
            "hero_start": "#ffffff",
            "hero_end": "#f0fdfa",
            "hero_border": "#99f6e4",
            "sidebar": "#0f172a",
            "sidebar_card": "#134e4a",
            "sidebar_card_border": "#0f766e",
            "soft_card": "#f0fdfa",
            "soft_border": "#99f6e4",
            "selected_bg": "#ccfbf1",
            "selected_border": "#0f766e",
            "primary": "#0f766e",
            "primary_hover": "#0d9488",
            "hover_bg": "#ccfbf1",
            "hover_border": "#5eead4",
            "compact_text": "#134e4a",
            "scroll": "#0f766e",
        },
    }
)


def build_stylesheet(theme: str = "light") -> str:
    tokens = _THEME_TOKENS.get(theme, _THEME_TOKENS["light"])
    return f"""
    QWidget {{
        background: {tokens['app_bg']};
        color: {tokens['text']};
        font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
        font-size: 13px;
    }}

    QLabel {{
        background: transparent;
    }}

    QMainWindow {{
        background: {tokens['transparent']};
    }}

    QWidget#RootSurface {{
        background: {tokens['transparent']};
    }}

    QFrame#AppShell {{
        background: {tokens['shell_bg']};
        border: 1px solid {tokens['titlebar_border']};
        border-radius: 16px;
    }}

    QWidget#ContentSurface {{
        background: {tokens['shell_bg']};
        border-bottom-left-radius: 16px;
        border-bottom-right-radius: 16px;
    }}

    QFrame#TitleBar {{
        background: {tokens['titlebar_bg']};
        border-top-left-radius: 16px;
        border-top-right-radius: 16px;
        border-bottom: 1px solid {tokens['titlebar_border']};
    }}

    QLabel#TitleText {{
        color: {tokens['titlebar_text']};
        font-size: 12px;
        font-weight: 650;
    }}

    QLabel#TitleIcon {{
        background: {tokens['titlebar_icon_bg']};
        border-radius: 8px;
        min-width: 22px;
        min-height: 22px;
        max-width: 22px;
        max-height: 22px;
    }}

    QPushButton#MinimizeButton,
    QPushButton#MaximizeButton,
    QPushButton#CloseButton {{
        min-width: 44px;
        max-width: 44px;
        min-height: 32px;
        max-height: 32px;
        padding: 0;
        border: none;
        border-radius: 8px;
        background: transparent;
        color: {tokens['titlebar_text']};
        font-size: 14px;
        font-weight: 700;
    }}

    QPushButton#MinimizeButton:hover,
    QPushButton#MaximizeButton:hover {{
        background: {tokens['titlebar_button_hover']};
    }}

    QPushButton#CloseButton:hover {{
        background: {tokens['titlebar_close_hover']};
        color: #ffffff;
    }}

    QLabel#AppTitle {{
        color: {tokens['sidebar_text']};
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 0.2px;
    }}

    QLabel#SidebarSubtitle {{
        color: {tokens['sidebar_muted']};
        font-size: 12px;
    }}

    QLabel#PageTitle {{
        color: {tokens['title']};
        font-size: 26px;
        font-weight: 800;
    }}

    QLabel#SectionTitle {{
        color: {tokens['title']};
        font-size: 15px;
        font-weight: 700;
    }}

    QLabel#MutedText {{
        color: {tokens['muted']};
        font-size: 12px;
    }}

    QLabel#SkillDescription {{
        color: {tokens['muted']};
        font-size: 11px;
        line-height: 14px;
    }}

    QLabel#StatValue {{
        color: {tokens['title']};
        font-size: 24px;
        font-weight: 800;
    }}

    QLabel#StatLabel {{
        color: {tokens['muted']};
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }}

    QFrame#Sidebar {{
        background: {tokens['sidebar']};
        border-radius: 24px;
    }}

    QFrame#Card {{
        background: {tokens['card']};
        border: 1px solid {tokens['card_border']};
        border-radius: 22px;
    }}

    QFrame#HeroCard {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {tokens['hero_start']}, stop:1 {tokens['hero_end']});
        border: 1px solid {tokens['hero_border']};
        border-radius: 26px;
    }}

    QFrame#SidebarCard {{
        background: {tokens['sidebar_card']};
        border: 1px solid {tokens['sidebar_card_border']};
        border-radius: 18px;
    }}

    QFrame#ActionBar {{
        background: transparent;
        border: none;
        border-radius: 0;
    }}

    QFrame#HarnessPrimaryActions,
    QFrame#HarnessProjectActions {{
        background: {tokens['soft_card']};
        border: 1px solid {tokens['soft_border']};
        border-radius: 16px;
    }}

    QFrame#ClientPill {{
        background: {tokens['pill_bg']};
        border: 1px solid {tokens['pill_border']};
        border-radius: 14px;
    }}

    QFrame#ClientCard {{
        background: {tokens['soft_card']};
        border: 1px solid {tokens['client_border']};
        border-radius: 16px;
    }}

    QFrame#ClientCardReady {{
        background: {tokens['ready_bg']};
        border: 1px solid {tokens['ready_border']};
        border-radius: 16px;
    }}

    QFrame#ClientCardSelected {{
        background: {tokens['selected_bg']};
        border: 2px solid {tokens['selected_border']};
        border-radius: 16px;
    }}

    QLabel#ClientName {{
        color: {tokens['title']};
        font-size: 13px;
        font-weight: 800;
    }}

    QLabel#ClientPath {{
        color: {tokens['client_path']};
        font-size: 11px;
    }}

    QLabel#ClientStatusReady {{
        color: {tokens['ready_text']};
        font-size: 11px;
        font-weight: 800;
    }}

    QLabel#ClientStatusMissing {{
        color: {tokens['missing_text']};
        font-size: 11px;
        font-weight: 800;
    }}

    QFrame#StatCard {{
        background: {tokens['soft_card']};
        border: 1px solid {tokens['soft_border']};
        border-radius: 18px;
    }}

    QFrame#HarnessListCard {{
        background: transparent;
        border: none;
        border-radius: 14px;
    }}

    QFrame#HarnessDeployBar {{
        background: transparent;
        border: none;
        border-radius: 16px;
    }}

    QFrame#HarnessDeployButtons {{
        background: {tokens['button_bg']};
        border: 1px solid {tokens['compact_border']};
        border-radius: 15px;
    }}

    QFrame#HarnessActions {{
        background: transparent;
        border: none;
    }}


    QLabel#HarnessCountPill {{
        color: {tokens['ready_text']};
        background: {tokens['ready_bg']};
        border: 1px solid {tokens['ready_border']};
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 850;
    }}

    QFrame#AssetLibraryItem {{
        background: transparent;
        border: none;
        border-radius: 0;
    }}

    QFrame#AssetLibraryActions {{
        background: transparent;
        border: none;
    }}

    QListWidget {{
        background: transparent;
        border: none;
        outline: 0;
        padding: 6px;
    }}

    QScrollArea#ClientSourceScroll {{
        background: transparent;
        border: none;
    }}

    QScrollArea#ClientSourceScroll > QWidget > QWidget {{
        background: transparent;
    }}

    QListWidget::item {{
        background: {tokens['soft_card']};
        border: 1px solid {tokens['soft_border']};
        border-radius: 14px;
        margin: 8px 0;
        padding: 10px;
        color: {tokens['list_text']};
    }}

    QListWidget::item:hover {{
        background: {tokens['hover_bg']};
        border-color: {tokens['hover_border']};
    }}

    QListWidget::item:selected {{
        background: {tokens['selected_bg']};
        border: 1px solid {tokens['primary']};
        color: {tokens['title']};
    }}

    QPushButton {{
        min-height: 34px;
        border-radius: 12px;
        border: 1px solid {tokens['button_border']};
        background: {tokens['button_bg']};
        color: {tokens['button_text']};
        font-weight: 650;
        padding: 7px 13px;
    }}

    QPushButton:hover {{
        background: {tokens['soft_card']};
        border-color: {tokens['hover_border']};
    }}

    QPushButton#PrimaryButton {{
        background: {tokens['primary']};
        border: 1px solid {tokens['primary']};
        color: #ffffff;
    }}

    QPushButton#PrimaryButton:hover {{
        background: {tokens['primary_hover']};
    }}

    QPushButton#SecondaryButton {{
        background: {tokens['secondary_bg']};
        border: 1px solid {tokens['hover_border']};
        color: {tokens['primary_hover']};
    }}

    QPushButton#CompactButton {{
        min-height: 30px;
        background: {tokens['button_bg']};
        border: 1px solid {tokens['compact_border']};
        color: {tokens['compact_text']};
        padding: 5px 11px;
    }}

    QPushButton#SourceDeleteButton {{
        min-height: 26px;
        background: transparent;
        border: 1px solid transparent;
        color: {tokens['danger_text']};
        font-size: 11px;
        padding: 3px 7px;
        font-weight: 600;
    }}

    QPushButton#SourceDeleteButton:hover {{
        background: {tokens['danger_hover']};
        border-color: {tokens['danger_border']};
    }}

    QPushButton#SourceImportButton {{
        min-height: 26px;
        background: transparent;
        border: 1px solid transparent;
        color: {tokens['primary_hover']};
        font-size: 11px;
        padding: 3px 7px;
        font-weight: 700;
    }}

    QPushButton#SourceImportButton:hover {{
        background: {tokens['hover_bg']};
        border-color: {tokens['hover_border']};
    }}

    QPushButton#IconButton,
    QPushButton#IconButtonChecked {{
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        padding: 0;
        border-radius: 14px;
        background: {tokens['button_bg']};
        border: 1px solid {tokens['compact_border']};
        color: {tokens['compact_text']};
        font-size: 17px;
        font-weight: 800;
    }}

    QPushButton#IconButton:hover {{
        background: {tokens['soft_card']};
        border-color: {tokens['hover_border']};
    }}

    QPushButton#HarnessDeployIconCodex,
    QPushButton#HarnessDeployIconCodexActive,
    QPushButton#HarnessDeployIconClaude,
    QPushButton#HarnessDeployIconClaudeActive,
    QPushButton#HarnessDeployIconOpenCode,
    QPushButton#HarnessDeployIconOpenCodeActive {{
        max-width: 24px;
        min-width: 24px;
        min-height: 24px;
        max-height: 24px;
        border-radius: 12px;
        background: {tokens['button_bg']};
        border: 1px solid {tokens['compact_border']};
        color: {tokens['muted']};
        font-size: 10px;
        font-weight: 900;
        padding: 0;
    }}

    QPushButton#HarnessDeployIconCodex:hover,
    QPushButton#HarnessDeployIconClaude:hover,
    QPushButton#HarnessDeployIconOpenCode:hover {{
        background: {tokens['hover_bg']};
        border-color: {tokens['hover_border']};
        color: {tokens['primary_hover']};
    }}

    QPushButton#HarnessDeployIconCodex {{
        color: #38bdf8;
        border-color: rgba(56, 189, 248, 0.42);
    }}

    QPushButton#HarnessDeployIconClaude {{
        color: #f59e0b;
        border-color: rgba(245, 158, 11, 0.42);
    }}

    QPushButton#HarnessDeployIconOpenCode {{
        color: #a78bfa;
        border-color: rgba(167, 139, 250, 0.42);
    }}

    QPushButton#HarnessDeployIconCodexActive,
    QPushButton#HarnessDeployIconClaudeActive,
    QPushButton#HarnessDeployIconOpenCodeActive {{
        background: {tokens['ready_bg']};
        border: 1px solid {tokens['ready_border']};
        color: {tokens['ready_text']};
    }}

    QPushButton#HarnessDeployIconCodexActive:hover,
    QPushButton#HarnessDeployIconClaudeActive:hover,
    QPushButton#HarnessDeployIconOpenCodeActive:hover {{
        background: {tokens['danger_hover']};
        border-color: {tokens['danger_border']};
        color: {tokens['danger_text']};
    }}

    QPushButton#IconButtonChecked {{
        background: {tokens['primary']};
        border: 1px solid {tokens['primary']};
        color: #ffffff;
    }}

    QPushButton#SegmentButton {{
        min-width: 92px;
        background: transparent;
        border: none;
        color: {tokens['muted']};
        font-weight: 800;
    }}

    QPushButton#SegmentButtonChecked {{
        min-width: 92px;
        background: {tokens['sidebar']};
        border: 1px solid {tokens['sidebar']};
        color: #ffffff;
        font-weight: 800;
    }}

    QPushButton#DangerButton {{
        background: {tokens['danger_bg']};
        border: 1px solid {tokens['danger_border']};
        color: {tokens['danger_text']};
    }}

    QPushButton#DangerButton:hover {{
        background: {tokens['danger_hover']};
    }}

    QPushButton#SidebarButton {{
        background: {tokens['primary_hover']};
        border: 1px solid #3b82f6;
        color: #eff6ff;
    }}

    QPushButton#DeployInstallButton {{
        min-width: 96px;
        max-width: 96px;
        background: {tokens['primary']};
        border: 1px solid {tokens['primary']};
        color: #ffffff;
    }}

    QPushButton#DeployUninstallButton {{
        min-width: 96px;
        max-width: 96px;
        background: {tokens['danger_bg']};
        border: 1px solid {tokens['danger_border']};
        color: {tokens['danger_text']};
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}

    QScrollBar::handle:vertical {{
        background: {tokens['scroll']};
        border-radius: 5px;
    }}
    """
