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


def build_stylesheet(theme: str = "light") -> str:
    if theme == "system":
        theme = "light"
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

    QFrame#DeployRow {{
        background: {tokens['soft_card']};
        border: 1px solid {tokens['soft_border']};
        border-radius: 16px;
    }}

    QFrame#AssetLibraryItem {{
        background: transparent;
        border: none;
        border-radius: 0;
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
