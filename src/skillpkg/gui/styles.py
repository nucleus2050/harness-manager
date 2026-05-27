from __future__ import annotations


def build_stylesheet() -> str:
    return """
    QWidget {
        background: #eef2f7;
        color: #111827;
        font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
        font-size: 13px;
    }

    QLabel {
        background: transparent;
    }

    QMainWindow {
        background: #eef2f7;
    }

    QLabel#AppTitle {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 0.2px;
    }

    QLabel#SidebarSubtitle {
        color: #94a3b8;
        font-size: 12px;
    }

    QLabel#PageTitle {
        color: #0f172a;
        font-size: 26px;
        font-weight: 800;
    }

    QLabel#SectionTitle {
        color: #0f172a;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#MutedText {
        color: #64748b;
        font-size: 12px;
    }

    QLabel#StatValue {
        color: #0f172a;
        font-size: 24px;
        font-weight: 800;
    }

    QLabel#StatLabel {
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }

    QFrame#Sidebar {
        background: #0f172a;
        border-radius: 24px;
    }

    QFrame#Card {
        background: #ffffff;
        border: 1px solid #dbe3ef;
        border-radius: 22px;
    }

    QFrame#HeroCard {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #e8f0ff);
        border: 1px solid #d9e5fb;
        border-radius: 26px;
    }

    QFrame#SidebarCard {
        background: #172554;
        border: 1px solid #1e3a8a;
        border-radius: 18px;
    }

    QFrame#ActionBar {
        background: transparent;
        border: none;
        border-radius: 0;
    }

    QFrame#ClientPill {
        background: #111c35;
        border: 1px solid #263a63;
        border-radius: 14px;
    }

    QFrame#ClientCard {
        background: #f8fafc;
        border: 1px solid #dbeafe;
        border-radius: 16px;
    }

    QFrame#ClientCardReady {
        background: #ecfdf5;
        border: 1px solid #86efac;
        border-radius: 16px;
    }

    QFrame#ClientCardSelected {
        background: #dbeafe;
        border: 2px solid #60a5fa;
        border-radius: 16px;
    }

    QLabel#ClientName {
        color: #0f172a;
        font-size: 13px;
        font-weight: 800;
    }

    QLabel#ClientPath {
        color: #475569;
        font-size: 11px;
    }

    QLabel#ClientStatusReady {
        color: #15803d;
        font-size: 11px;
        font-weight: 800;
    }

    QLabel#ClientStatusMissing {
        color: #b45309;
        font-size: 11px;
        font-weight: 800;
    }

    QFrame#StatCard {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
    }

    QFrame#DeployRow {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
    }

    QListWidget {
        background: transparent;
        border: none;
        outline: 0;
        padding: 4px;
    }

    QListWidget::item {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        margin: 5px 0;
        padding: 12px;
        color: #172033;
    }

    QListWidget::item:hover {
        background: #eff6ff;
        border-color: #bfdbfe;
    }

    QListWidget::item:selected {
        background: #dbeafe;
        border: 1px solid #2563eb;
        color: #0f172a;
    }

    QPushButton {
        min-height: 34px;
        border-radius: 12px;
        border: 1px solid #d0d8e6;
        background: #ffffff;
        color: #1f2937;
        font-weight: 650;
        padding: 7px 13px;
    }

    QPushButton:hover {
        background: #f8fafc;
        border-color: #93c5fd;
    }

    QPushButton#PrimaryButton {
        background: #2563eb;
        border: 1px solid #2563eb;
        color: #ffffff;
    }

    QPushButton#PrimaryButton:hover {
        background: #1d4ed8;
    }

    QPushButton#SecondaryButton {
        background: #eaf1ff;
        border: 1px solid #bfdbfe;
        color: #1d4ed8;
    }

    QPushButton#CompactButton {
        min-height: 30px;
        background: #ffffff;
        border: 1px solid #cbd5e1;
        color: #334155;
        padding: 5px 11px;
    }

    QPushButton#SegmentButton {
        min-width: 92px;
        background: transparent;
        border: none;
        color: #64748b;
        font-weight: 800;
    }

    QPushButton#SegmentButtonChecked {
        min-width: 92px;
        background: #0f172a;
        border: 1px solid #0f172a;
        color: #ffffff;
        font-weight: 800;
    }

    QPushButton#DangerButton {
        background: #fff7f7;
        border: 1px solid #fecaca;
        color: #b91c1c;
    }

    QPushButton#DangerButton:hover {
        background: #fee2e2;
    }

    QPushButton#SidebarButton {
        background: #1d4ed8;
        border: 1px solid #3b82f6;
        color: #eff6ff;
    }

    QPushButton#DeployInstallButton {
        min-width: 96px;
        max-width: 96px;
        background: #2563eb;
        border: 1px solid #2563eb;
        color: #ffffff;
    }

    QPushButton#DeployUninstallButton {
        min-width: 96px;
        max-width: 96px;
        background: #fff7f7;
        border: 1px solid #fecaca;
        color: #b91c1c;
    }

    QScrollBar:vertical {
        background: transparent;
        width: 10px;
        margin: 2px;
    }

    QScrollBar::handle:vertical {
        background: #cbd5e1;
        border-radius: 5px;
    }
    """
