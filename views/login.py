import flet as ft
from api import login
from storage import save_tokens

def login_view(page: ft.Page, go):
    page.title = 'UniFind — Login'

    username = ft.TextField(label='Username', prefix_icon=ft.Icons.PERSON)
    password = ft.TextField(label='Password', password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
    error    = ft.Text('', color=ft.Colors.RED_600, size=13)
    loading  = ft.ProgressRing(visible=False, width=20, height=20)

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
        ft.Container(
            content=ft.Column([
                ft.Text('UniFind', size=28, weight=ft.FontWeight.BOLD, color='#5c4f3a'),
                ft.Text('University of Mauritius', size=13, color='#7a7670'),
                ft.Divider(height=20, color='transparent'),
                ft.Text('Welcome back', size=20, weight=ft.FontWeight.W_600),
                ft.Text('Log in to your account', size=13, color='#7a7670'),
                ft.Divider(height=16, color='transparent'),
                username,
                password,
                error,
                ft.Divider(height=8, color='transparent'),
                ft.Row([loading, ft.ElevatedButton(
                    'Log In',
                    on_click=do_login,
                    bgcolor='#5c4f3a',
                    color='white',
                    width=300,
                    height=44,
                )], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=8, color='transparent'),
                ft.Row([
                    ft.Text("Don't have an account?", size=13),
                    ft.TextButton('Register', on_click=lambda e: go('register')),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10),
            padding=40,
            width=400,
            bgcolor='white',
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.08, 'black')),
        )
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)