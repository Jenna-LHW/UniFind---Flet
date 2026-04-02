import flet as ft
from api import get_user
from storage import load_tokens, clear_tokens

def profile_view(page: ft.Page, go):
    access, _ = load_tokens()
    if not access:
        go('login')
        return ft.Text('')

    status, user = get_user()

    if status != 200:
        clear_tokens()
        go('login')
        return ft.Text('')

    def do_logout(e):
        clear_tokens()
        go('login')

    def field_row(label, value):
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=13, color='#7a7670', width=120),
                ft.Text(value or '—', size=14, color='#2c2c2a', weight=ft.FontWeight.W_500),
            ]),
            padding=ft.Padding.symmetric(vertical=10),
            border=ft.Border.only(bottom=ft.BorderSide(1, '#f0ece6')),
        )

    return ft.Column([

        # Header card
        ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(user.get('username', '?')[0].upper(),
                                    size=24, weight=ft.FontWeight.BOLD, color='white'),
                    width=56, height=56,
                    bgcolor='#5c4f3a',
                    border_radius=28,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(user.get('username', ''), size=18, weight=ft.FontWeight.BOLD, color='#2c2c2a'),
                    ft.Container(
                        content=ft.Text(user.get('role', '').capitalize(), size=11,
                                        weight=ft.FontWeight.BOLD, color='#5c4f3a'),
                        bgcolor='#e8e2d9',
                        padding=ft.Padding.symmetric(horizontal=10, vertical=3),
                        border_radius=20,
                    ),
                ], spacing=6),
            ], spacing=16),
            padding=24,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),

        # Info card
        ft.Container(
            content=ft.Column([
                ft.Text('Account Information', size=14, weight=ft.FontWeight.W_600,
                        color='#5c4f3a'),
                ft.Divider(height=12, color='transparent'),
                field_row('Username',     user.get('username')),
                field_row('Email',        user.get('email')),
                field_row('First Name',   user.get('first_name')),
                field_row('Last Name',    user.get('last_name')),
                field_row('Role',         user.get('role', '').capitalize()),
                field_row('Phone',        user.get('phone')),
                field_row('Student ID',   user.get('student_id')),
            ], spacing=0),
            padding=24,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),

        # Actions
        ft.Row([
            ft.ElevatedButton(
                'Log Out',
                icon=ft.Icons.LOGOUT,
                bgcolor='#e8e2d9',
                color='#5c4f3a',
                on_click=do_logout,
            ),
        ]),

    ], spacing=16, scroll=ft.ScrollMode.AUTO)