import flet as ft

BROWN      = '#5c4f3a'
LIGHT_BG   = '#f5f2ee'
CARD_BG    = 'white'
BORDER_CLR = '#d6d1c8'
MUTED      = '#7a7670'
DARK       = '#2c2c2a'


def about_view(page: ft.Page, go):

    def card(icon, title, *children):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=BROWN, size=20),
                    ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=BROWN),
                ], spacing=10),
                ft.Divider(height=1, color=BORDER_CLR),
                *list(children),
            ], spacing=10),
            padding=20,
            bgcolor=CARD_BG,
            border_radius=12,
            border=ft.Border.all(1, BORDER_CLR),
        )

    def mission_item(icon, text):
        return ft.Row([
            ft.Container(
                content=ft.Icon(icon, color=BROWN, size=18),
                width=36, height=36,
                bgcolor='#f0ece6',
                border_radius=18,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Text(text, size=13, color=DARK, expand=True),
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START)

    def feature_item(icon, label, desc):
        return ft.Row([
            ft.Container(
                content=ft.Icon(icon, color='white', size=16),
                width=32, height=32,
                bgcolor=BROWN,
                border_radius=8,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Column([
                ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=DARK),
                ft.Text(desc, size=12, color=MUTED),
            ], spacing=2, expand=True),
        ], spacing=12)

    def team_member(initials, name, role):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(initials, size=18, weight=ft.FontWeight.BOLD, color='white'),
                    width=52, height=52, bgcolor=BROWN,
                    border_radius=26, alignment=ft.Alignment(0, 0),
                ),
                ft.Text(name, size=13, weight=ft.FontWeight.W_600, color=DARK, text_align=ft.TextAlign.CENTER),
                ft.Text(role, size=11, color=MUTED, text_align=ft.TextAlign.CENTER),
            ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16,
            bgcolor=LIGHT_BG,
            border_radius=12,
            border=ft.Border.all(1, BORDER_CLR),
            expand=True,
        )

    return ft.Column([

        # Header banner
        ft.Container(
            content=ft.Column([
                ft.Image(src='logo.png', width=72, height=72),
                ft.Text('About UniFind', size=22, weight=ft.FontWeight.BOLD, color=DARK),
                ft.Text('Learn about our platform and how it helps the UoM community.',
                        size=13, color=MUTED, text_align=ft.TextAlign.CENTER),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.symmetric(vertical=28, horizontal=20),
            bgcolor=CARD_BG,
            border_radius=12,
            border=ft.Border.all(1, BORDER_CLR),
            alignment=ft.Alignment(0, 0),
        ),

        # About the platform
        card(
            ft.Icons.LAYERS_OUTLINED,
            'About the Platform',
            ft.Text(
                'UniFind is a centralized Lost & Found management system designed for the '
                'University of Mauritius community. It provides a structured and reliable way '
                'for students and staff to report, search, and recover lost items. By replacing '
                'scattered communication methods with a single platform, UniFind ensures items '
                'are properly documented, easy to access, and managed efficiently.',
                size=13, color=DARK,
            ),
        ),

        # Mission
        card(
            ft.Icons.FLAG_OUTLINED,
            'Our Mission',
            mission_item(ft.Icons.EDIT_NOTE,
                         'Simplify the reporting of lost and found items for the entire university community.'),
            mission_item(ft.Icons.HANDSHAKE_OUTLINED,
                         'Promote honesty and responsibility within the campus community.'),
            mission_item(ft.Icons.SHIELD_OUTLINED,
                         'Ensure items are returned securely through a verified, admin-assisted process.'),
            mission_item(ft.Icons.SEARCH,
                         'Provide a fast and searchable record of all reported items.'),
        ),

        # Key features
        card(
            ft.Icons.STAR_OUTLINE,
            'Key Features',
            feature_item(ft.Icons.REPORT_OUTLINED,      'Report Lost Items',   'Submit details and photos of lost belongings.'),
            feature_item(ft.Icons.INVENTORY_2_OUTLINED, 'Report Found Items',  'Log items you\'ve discovered on campus.'),
            feature_item(ft.Icons.SEARCH,               'Browse & Search',     'Filter items by category, date, and status.'),
            feature_item(ft.Icons.TASK_ALT_OUTLINED,    'Submit Claims',       'Claim an item by providing proof of ownership.'),
            feature_item(ft.Icons.NOTIFICATIONS_OUTLINED,'Notifications',      'Get real-time alerts on your reported items.'),
            feature_item(ft.Icons.STAR_OUTLINED,        'Community Reviews',   'Share feedback about the UniFind experience.'),
        ),

        # How it works
        card(
            ft.Icons.HELP_OUTLINE,
            'How It Works',
            ft.Text('1. Register or log in with your university credentials.', size=13, color=DARK),
            ft.Text('2. Report a lost item or a found item with details and a photo.', size=13, color=DARK),
            ft.Text('3. Browse the listings — if you spot your item, submit a claim.', size=13, color=DARK),
            ft.Text('4. An admin reviews the claim and facilitates the handover.', size=13, color=DARK),
            ft.Text('5. Both parties are notified once the item is resolved.', size=13, color=DARK),
        ),

        # Contact / footer
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.MAIL_OUTLINE, color=BROWN, size=16),
                    ft.Text('Questions? Contact us via the Contact page.',
                            size=13, color=MUTED),
                ], spacing=8),
                ft.TextButton(
                    'Go to Contact →',
                    on_click=lambda e: go('contact'),
                    style=ft.ButtonStyle(color=BROWN),
                ),
            ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=CARD_BG,
            border_radius=12,
            border=ft.Border.all(1, BORDER_CLR),
            alignment=ft.Alignment(0, 0),
        ),

    ], spacing=16, scroll=ft.ScrollMode.AUTO)
