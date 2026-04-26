import flet as ft
from api import login
from storage import save_tokens

BROWN = '#5c4f3a'
LIGHT = '#f5f2ee'

def login_view(page: ft.Page, go):
    page.title = 'UniFind — Login'

    username = ft.TextField(
        label='Username',
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=12,
        filled=True,
        bgcolor='white',
        border_color='#d6d1c8',
        focused_border_color=BROWN,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )
    password = ft.TextField(
        label='Password',
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=12,
        filled=True,
        bgcolor='white',
        border_color='#d6d1c8',
        focused_border_color=BROWN,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )
    error   = ft.Text('', color=ft.Colors.RED_600, size=13, text_align=ft.TextAlign.CENTER)
    loading = ft.ProgressRing(visible=False, width=22, height=22, color=BROWN)

    def do_login(e):
        error.value = ''
        if not username.value or not password.value:
            error.value = 'Please fill in all fields.'
            page.update()
            return
        loading.visible = True
        page.update()
        status, data = login(username.value.strip(), password.value)
        loading.visible = False
        if status == 200:
            save_tokens(data['access'], data['refresh'])
            go('home')
        else:
            error.value = 'Invalid username or password.'
            page.update()

    return ft.Column([
        ft.Container(expand=True),  # push card to vertical center

        # Logo + branding
        ft.Column([
            ft.Container(
                content=ft.Image(src='logo.png', fit='contain'),
                width=72, height=72,
                border_radius=20,
                bgcolor='white',
                shadow=ft.BoxShadow(blur_radius=16, color='#1a000000'),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Text('UniFind', size=28, weight=ft.FontWeight.BOLD, color=BROWN),
            ft.Text('University of Mauritius', size=13, color='#9a8f80'),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),

        ft.Container(height=32),

        # Card 
        ft.Container(
            content=ft.Column([
                ft.Text('Welcome back', size=20, weight=ft.FontWeight.W_700, color='#2c2c2a'),
                ft.Text('Sign in to your account', size=13, color='#9a8f80'),
                ft.Container(height=8),
                username,
                password,
                error,
                ft.Container(height=4),
                ft.Container(
                    content=ft.Row([
                        loading,
                        ft.ElevatedButton(
                            'Log In',
                            on_click=do_login,
                            bgcolor=BROWN,
                            color='white',
                            height=50,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=14),
                            ),
                            expand=True,
                        ),
                    ], spacing=10),
                ),
            ], spacing=12),
            padding=ft.padding.symmetric(horizontal=24, vertical=28),
            bgcolor='white',
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color='#14000000', offset=ft.Offset(0, 4)),
        ),

        ft.Container(height=20),

        ft.Row([
            ft.Text("Don't have an account?", size=13, color='#7a7670'),
            ft.TextButton(
                'Register',
                on_click=lambda e: go('register'),
                style=ft.ButtonStyle(color=BROWN),
            ),
        ], alignment=ft.MainAxisAlignment.CENTER),

        ft.Container(expand=True),
    ],
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    expand=True,
    )
