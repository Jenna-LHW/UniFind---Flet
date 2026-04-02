import flet as ft
from api import register
from storage import save_tokens
from api import login

ROLES = [('student', 'Student'), ('staff', 'Staff')]
CATEGORIES = ['Electronics','Clothing','Accessories','Books & Stationery','ID & Cards','Bags','Keys','Other']

def register_view(page: ft.Page, go):
    page.title = 'UniFind — Register'

    username   = ft.TextField(label='Username', prefix_icon=ft.Icons.PERSON)
    email      = ft.TextField(label='UoM Email (@uom.ac.mu)', prefix_icon=ft.Icons.EMAIL)
    role       = ft.Dropdown(label='Role', options=[ft.dropdown.Option(k, v) for k, v in ROLES])
    student_id = ft.TextField(label='Student ID (if student)', prefix_icon=ft.Icons.BADGE)
    phone      = ft.TextField(label='Phone', prefix_icon=ft.Icons.PHONE)
    password   = ft.TextField(label='Password', password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
    password2  = ft.TextField(label='Confirm Password', password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
    error      = ft.Text('', color=ft.Colors.RED_600, size=13)
    success    = ft.Text('', color=ft.Colors.GREEN_600, size=13)
    loading    = ft.ProgressRing(visible=False, width=20, height=20)

    def do_register(e):
        error.value   = ''
        success.value = ''

        if not all([username.value, email.value, role.value, password.value, password2.value]):
            error.value = 'Please fill in all required fields.'
            page.update()
            return

        if not email.value.endswith('@uom.ac.mu'):
            error.value = 'Only UoM email addresses are allowed.'
            page.update()
            return

        if password.value != password2.value:
            error.value = 'Passwords do not match.'
            page.update()
            return

        loading.visible = True
        page.update()

        data = {
            'username':   username.value.strip(),
            'email':      email.value.strip(),
            'role':       role.value,
            'student_id': student_id.value.strip(),
            'phone':      phone.value.strip(),
            'password':   password.value,
        }

        status, resp = register(data)
        loading.visible = False

        if status == 201:
            # Auto login after register
            s2, tokens = login(username.value.strip(), password.value)
            if s2 == 200:
                save_tokens(tokens['access'], tokens['refresh'])
                go('home')
            else:
                success.value = 'Registered! Please log in.'
                go('login')
        else:
            msgs = []
            for field, errs in resp.items():
                msgs.append(f"{field}: {errs[0] if isinstance(errs, list) else errs}")
            error.value = '\n'.join(msgs)
            page.update()

    return ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Text('UniFind', size=28, weight=ft.FontWeight.BOLD, color='#5c4f3a'),
                ft.Text('University of Mauritius', size=13, color='#7a7670'),
                ft.Divider(height=16, color='transparent'),
                ft.Text('Create your account', size=20, weight=ft.FontWeight.W_600),
                ft.Divider(height=10, color='transparent'),
                username, email, role, student_id, phone, password, password2,
                error, success,
                ft.Divider(height=8, color='transparent'),
                ft.Row([loading, ft.ElevatedButton(
                    'Register',
                    on_click=do_register,
                    bgcolor='#5c4f3a',
                    color='white',
                    width=300,
                    height=44,
                )], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    ft.Text('Already have an account?', size=13),
                    ft.TextButton('Log In', on_click=lambda e: go('login')),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO),
            padding=40,
            width=420,
            bgcolor='white',
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.08, 'black')),
        )
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)