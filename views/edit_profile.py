import flet as ft
from api import get_user, update_profile
from storage import load_tokens

BROWN      = '#5c4f3a'
LIGHT_BG   = '#f5f2ee'
CARD_BG    = 'white'
BORDER_CLR = '#d6d1c8'
DIVIDER    = '#f0ece6'
MUTED      = '#7a7670'
DARK       = '#2c2c2a'


def edit_profile_view(page: ft.Page, go):
    access, _ = load_tokens()
    if not access:
        go('login')
        return ft.Text('')

    status, user = get_user()
    if status != 200:
        go('login')
        return ft.Container()

    # ── Form fields ──────────────────────────────────────────
    first_name  = ft.TextField(label='First Name',  value=user.get('first_name', ''),  border_color=BORDER_CLR)
    last_name   = ft.TextField(label='Last Name',   value=user.get('last_name', ''),   border_color=BORDER_CLR)
    email       = ft.TextField(label='Email',       value=user.get('email', ''),       border_color=BORDER_CLR, keyboard_type=ft.KeyboardType.EMAIL)
    phone       = ft.TextField(label='Phone',       value=user.get('phone', ''),       border_color=BORDER_CLR, keyboard_type=ft.KeyboardType.PHONE)
    student_id  = ft.TextField(label='Student ID',  value=user.get('student_id', ''), border_color=BORDER_CLR)
    password    = ft.TextField(label='New Password (leave blank to keep current)', password=True, can_reveal_password=True, border_color=BORDER_CLR)
    confirm_pw  = ft.TextField(label='Confirm New Password', password=True, can_reveal_password=True, border_color=BORDER_CLR)

    error_text   = ft.Text('', color=ft.Colors.RED_600,   size=13)
    success_text = ft.Text('', color=ft.Colors.GREEN_600, size=13)

    saving = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

    def do_save(e):
        error_text.value   = ''
        success_text.value = ''

        if password.value and password.value != confirm_pw.value:
            error_text.value = 'Passwords do not match.'
            page.update()
            return

        saving.visible = True
        page.update()

        payload = {
            'first_name': first_name.value.strip(),
            'last_name':  last_name.value.strip(),
            'email':      email.value.strip(),
            'phone':      phone.value.strip(),
            'student_id': student_id.value.strip(),
        }
        if password.value:
            payload['password'] = password.value

        s, resp = update_profile(payload)
        saving.visible = False

        if s == 200:
            success_text.value = 'Profile updated successfully!'
            password.value    = ''
            confirm_pw.value  = ''
        else:
            # Show first error message from response
            if isinstance(resp, dict):
                msgs = []
                for k, v in resp.items():
                    msgs.append(f"{k}: {v[0] if isinstance(v, list) else v}")
                error_text.value = '\n'.join(msgs)
            else:
                error_text.value = 'Update failed. Please try again.'

        page.update()

    def card(*children):
        return ft.Container(
            content=ft.Column(list(children), spacing=12),
            padding=24,
            bgcolor=CARD_BG,
            border_radius=12,
            border=ft.Border.all(1, BORDER_CLR),
        )

    def section_header(icon, label):
        return ft.Row([
            ft.Icon(icon, color=BROWN, size=18),
            ft.Text(label, size=14, weight=ft.FontWeight.W_600, color=BROWN),
        ], spacing=8)

    return ft.Column([

        # Page title
        ft.Row([
            ft.IconButton(
                ft.Icons.ARROW_BACK,
                icon_color=BROWN,
                tooltip='Back to Profile',
                on_click=lambda e: go('profile'),
            ),
            ft.Text('Edit Profile', size=20, weight=ft.FontWeight.BOLD, color=DARK),
        ], spacing=4),

        # Personal info card
        card(
            section_header(ft.Icons.PERSON_OUTLINE, 'Personal Information'),
            first_name,
            last_name,
            email,
            phone,
            student_id,
        ),

        # Password card
        card(
            section_header(ft.Icons.LOCK_OUTLINE, 'Change Password'),
            ft.Text('Leave blank to keep your current password.',
                    size=12, color=MUTED, italic=True),
            password,
            confirm_pw,
        ),

        # Feedback
        error_text,
        success_text,

        # Actions
        ft.Row([
            ft.ElevatedButton(
                'Save Changes',
                icon=ft.Icons.SAVE_OUTLINED,
                bgcolor=BROWN,
                color='white',
                on_click=do_save,
            ),
            saving,
            ft.OutlinedButton(
                'Cancel',
                on_click=lambda e: go('profile'),
            ),
        ], spacing=12),

    ], spacing=16, scroll=ft.ScrollMode.AUTO)
