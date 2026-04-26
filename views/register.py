import flet as ft
from api import register
from storage import save_tokens
from api import login

BROWN = '#5c4f3a'
ROLES = [('student', 'Student'), ('staff', 'Staff')]

def _field(label, icon, password=False, reveal=False, hint=None):
    return ft.TextField(
        label=label,
        prefix_icon=icon,
        password=password,
        can_reveal_password=reveal,
        hint_text=hint,
        border_radius=12,
        filled=True,
        bgcolor='white',
        border_color='#d6d1c8',
        focused_border_color=BROWN,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )

def register_view(page: ft.Page, go):
    page.title = 'UniFind — Register'

    username   = _field('Username', ft.Icons.PERSON_OUTLINE)
    email      = _field('UoM Email', ft.Icons.EMAIL_OUTLINED, hint='you@uom.ac.mu')
    role       = ft.Dropdown(
        label='Role',
        options=[ft.dropdown.Option(k, v) for k, v in ROLES],
        border_radius=12,
        filled=True,
        bgcolor='white',
        border_color='#d6d1c8',
        focused_border_color=BROWN,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )
    student_id = _field('Student ID (if student)', ft.Icons.BADGE_OUTLINED)
    phone      = _field('Phone', ft.Icons.PHONE_OUTLINED)
    password   = _field('Password', ft.Icons.LOCK_OUTLINE, password=True, reveal=True)
    password2  = _field('Confirm Password', ft.Icons.LOCK_OUTLINE, password=True, reveal=True)
    error      = ft.Text('', color=ft.Colors.RED_600, size=13)
    success    = ft.Text('', color=ft.Colors.GREEN_600, size=13)
    loading    = ft.ProgressRing(visible=False, width=22, height=22, color=BROWN)

    def do_register(e):
        error.value = ''
        success.value = ''
        if not all([username.value, email.value, role.value, password.value, password2.value]):
            error.value = 'Please fill in all required fields.'
            page.update(); return
        if not email.value.endswith('@uom.ac.mu'):
            error.value = 'Only UoM email addresses are allowed.'
            page.update(); return
        if password.value != password2.value:
            error.value = 'Passwords do not match.'
            page.update(); return

        loading.visible = True; page.update()
        data = {
            'username': username.value.strip(), 'email': email.value.strip(),
            'role': role.value, 'student_id': student_id.value.strip(),
            'phone': phone.value.strip(), 'password': password.value,
        }
        status, resp = register(data)
        loading.visible = False
        if status == 201:
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
        # Header
        ft.Column([
            ft.Container(
                content=ft.Image(src='logo.png', fit='contain'),
                width=60, height=60,
                border_radius=16,
                bgcolor='white',
                shadow=ft.BoxShadow(blur_radius=12, color='#1a000000'),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Text('Create Account', size=24, weight=ft.FontWeight.BOLD, color=BROWN),
            ft.Text('Join the UniFind community', size=13, color='#9a8f80'),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),

        ft.Container(height=8),

        # Form card
        ft.Container(
            content=ft.Column([
                ft.Text('Personal Info', size=12, weight=ft.FontWeight.W_600,
                        color='#9a8f80', style=ft.TextStyle(letter_spacing=0.8)),
                username, email, role, student_id, phone,
                ft.Container(height=4),
                ft.Text('Security', size=12, weight=ft.FontWeight.W_600,
                        color='#9a8f80', style=ft.TextStyle(letter_spacing=0.8)),
                password, password2,
                error, success,
                ft.Container(height=4),
                ft.Row([
                    loading,
                    ft.ElevatedButton(
                        'Create Account',
                        on_click=do_register,
                        bgcolor=BROWN, color='white',
                        height=50, expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
                    ),
                ], spacing=10),
            ], spacing=12),
            padding=ft.padding.symmetric(horizontal=24, vertical=24),
            bgcolor='white',
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color='#14000000', offset=ft.Offset(0, 4)),
        ),

        ft.Row([
            ft.Text('Already have an account?', size=13, color='#7a7670'),
            ft.TextButton('Log In', on_click=lambda e: go('login'),
                         style=ft.ButtonStyle(color=BROWN)),
        ], alignment=ft.MainAxisAlignment.CENTER),

    ], spacing=16, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
