from __future__ import annotations

from skillpkg.gui.styles import build_stylesheet


def test_stylesheet_defines_modern_theme_tokens():
    stylesheet = build_stylesheet()

    assert "#0f172a" in stylesheet
    assert "#2563eb" in stylesheet
    assert "QFrame#Sidebar" in stylesheet
    assert "QFrame#Card" in stylesheet
    assert "QPushButton#PrimaryButton" in stylesheet


def test_stylesheet_styles_list_items_and_danger_buttons():
    stylesheet = build_stylesheet()

    assert "QListWidget::item:selected" in stylesheet
    assert "QPushButton#DangerButton" in stylesheet
    assert "border-radius" in stylesheet


def test_stylesheet_removes_label_background_blocks_and_adds_compact_buttons():
    stylesheet = build_stylesheet()

    assert "QLabel {" in stylesheet
    assert "background: transparent" in stylesheet
    assert "QPushButton#CompactButton" in stylesheet
    assert "QFrame#ActionBar" in stylesheet
    assert "QFrame#DeployRow" in stylesheet


def test_stylesheet_has_client_cards_and_deploy_buttons():
    stylesheet = build_stylesheet()

    assert "QFrame#ClientCard" in stylesheet
    assert "QLabel#ClientName" in stylesheet
    assert "QLabel#ClientPath" in stylesheet
    assert "QPushButton#DeployInstallButton" in stylesheet
    assert "QPushButton#DeployUninstallButton" in stylesheet
