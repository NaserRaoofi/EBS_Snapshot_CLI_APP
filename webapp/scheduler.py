import flet as ft

def scheduler_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    # Dummy future options (disabled for now)
    instance_dropdown = ft.Dropdown(
        label="🖥️ Select EC2 Instance",
        width=460,
        options=[
            ft.dropdown.Option("i-0123abcd - app-server"),
            ft.dropdown.Option("i-0456efgh - db-server"),
        ],
        value=None,
        disabled=True
    )

    frequency_dropdown = ft.Dropdown(
        label="⏱️ Schedule Frequency",
        width=460,
        options=[
            ft.dropdown.Option("Daily at 00:00 UTC"),
            ft.dropdown.Option("Weekly on Sunday"),
            ft.dropdown.Option("Custom (cron expression)")
        ],
        value="Daily at 00:00 UTC",
        disabled=True
    )

    cron_input = ft.TextField(
        label="🧮 Custom Cron Expression",
        hint_text="e.g., 0 2 * * * for daily at 2AM",
        disabled=True,
        width=460
    )

    status_preview = ft.Text(
        "⚠️ No schedule created yet.",
        size=14,
        italic=True,
        color=ft.Colors.RED_400
    )

    create_button = ft.ElevatedButton(
        "📆 Create Snapshot Schedule",
        icon="schedule",
        disabled=True,
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE
        )
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("⏱️ Snapshot Scheduler", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
            ft.Text("Plan automatic EC2 backups on a schedule", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_300),

            ft.Column([
                instance_dropdown,
                frequency_dropdown,
                cron_input
            ], spacing=20),

            ft.Divider(height=20),

            ft.Row([
                status_preview,
                ft.Container(content=create_button, padding=ft.padding.only(left=20))
            ], alignment=ft.MainAxisAlignment.CENTER),

        ], spacing=28),
        padding=32,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18
    )
