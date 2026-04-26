import flet as ft

BROWN = '#5c4f3a'
GREEN = '#3b5c38'

def about_view(page: ft.Page, go):
    page.title = 'About UniFind'

    def _feature(icon, title, desc, color=BROWN):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color='white', size=18),
                    width=44, height=44,
                    bgcolor=color,
                    border_radius=12,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(title, size=13, weight=ft.FontWeight.W_600, color='#2c2c2a'),
                    ft.Text(desc, size=11, color='#7a7670'),
                ], spacing=2, expand=True),
            ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            bgcolor='white', border_radius=14,
            border=ft.border.all(1, '#e8e2da'),
        )

    return ft.Column([

        # Hero
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Image(src='logo.png', fit='contain'),
                    width=72, height=72,
                    border_radius=20,
                    bgcolor='white',
                    shadow=ft.BoxShadow(blur_radius=16, color='#1a000000'),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text('UniFind', size=26, weight=ft.FontWeight.BOLD, color=BROWN),
                ft.Text('University of Mauritius', size=13, color='#9a8f80'),
                ft.Container(
                    content=ft.Text('v1.0.0', size=11, color=BROWN, weight=ft.FontWeight.W_500),
                    bgcolor='#ede8e0',
                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    border_radius=20,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=ft.padding.symmetric(vertical=28, horizontal=20),
            bgcolor='#ede9e3',
            border_radius=20,
            alignment=ft.Alignment(0, 0),
        ),

        # About text
        ft.Container(
            content=ft.Column([
                ft.Text('About', size=14, weight=ft.FontWeight.W_600, color='#2c2c2a'),
                ft.Text(
                    'UniFind is the official lost and found platform for the University of '
                    'Mauritius community. Our mission is to help students and staff quickly '
                    'reunite with their lost belongings through a simple, secure, and '
                    'community-driven reporting system.',
                    size=13, color='#5c5a55',
                ),
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=16, vertical=16),
            bgcolor='white', border_radius=14,
            border=ft.border.all(1, '#e8e2da'),
        ),

        # Features
        ft.Text('Features', size=14, weight=ft.FontWeight.W_600, color='#2c2c2a'),
        _feature(ft.Icons.PHOTO_CAMERA_OUTLINED,  'Photo Reports',
                 'Attach photos to help identify items quickly.', BROWN),
        _feature(ft.Icons.NOTIFICATIONS_OUTLINED, 'Smart Notifications',
                 'Get notified when a potential match is found.', '#c07830'),
        _feature(ft.Icons.COMPARE_ARROWS_ROUNDED, 'AI Matching',
                 'Automated matching between lost and found items.', '#7a5030'),
        _feature(ft.Icons.VERIFIED_USER_OUTLINED, 'UoM Verified',
                 'Only UoM email accounts can register.', GREEN),
        _feature(ft.Icons.STAR_OUTLINE_ROUNDED,   'Community Reviews',
                 'Rate your experience and help improve the service.', '#4a6e47'),

        # Footer
        ft.Container(
            content=ft.Column([
                ft.Text('Contact', size=13, weight=ft.FontWeight.W_600, color='#2c2c2a'),
                ft.Row([
                    ft.Icon(ft.Icons.EMAIL_OUTLINED, size=14, color='#9a8f80'),
                    ft.Text('unifind@uom.ac.mu', size=12, color='#7a7670'),
                ], spacing=6),
                ft.Divider(height=1, color='#f0ece6'),
                ft.Text('© 2025 UniFind · University of Mauritius',
                        size=11, color='#9a8f80', text_align=ft.TextAlign.CENTER),
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, bgcolor='white', border_radius=14,
            border=ft.border.all(1, '#e8e2da'),
        ),

        ft.Container(height=8),

    ], spacing=12, scroll=ft.ScrollMode.AUTO)
