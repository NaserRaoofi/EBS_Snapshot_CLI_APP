import flet as ft
from .backup import backup_panel
from .restore import restore_panel
from .list_snapshots import list_snapshots_panel
from .settings import settings_panel
from .iam import iam_panel
from .export import export_panel
from .scheduler import scheduler_panel

def main(page: ft.Page):
    page.title = "EC2 Snapshot Management Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.padding = 20

    panels = [
        backup_panel(page),
        restore_panel(page),
        list_snapshots_panel(page),
        settings_panel(page),
        iam_panel(page),
        export_panel(page),
        scheduler_panel(page)
    ]

    animated_container = ft.AnimatedSwitcher(content=panels[0], expand=True, transition=ft.AnimatedSwitcherTransition.FADE)

    def on_nav_change(e):
        nav_rail = sidebar.content  # NavigationRail is inside the Container
        animated_container.content = panels[nav_rail.selected_index]
        page.update()

    sidebar = ft.Container(
        content=ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon="backup", label="Backup"),
                ft.NavigationRailDestination(icon="restore", label="Restore"),
                ft.NavigationRailDestination(icon="list", label="Snapshots"),
                ft.NavigationRailDestination(icon="settings", label="Settings"),
                ft.NavigationRailDestination(icon="verified_user", label="IAM"),
                ft.NavigationRailDestination(icon="download", label="Export"),
                ft.NavigationRailDestination(icon="schedule", label="Schedule")
            ],
            on_change=on_nav_change
        ),
        height=600
    )

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("📦 EC2 Snapshot Tool", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([
                    sidebar,
                    ft.VerticalDivider(width=1),
                    animated_container
                ], expand=True)
            ], spacing=20),
            padding=20
        )
    )
