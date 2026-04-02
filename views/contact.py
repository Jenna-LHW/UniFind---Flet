import flet as ft
from api import send_contact, get_user
from storage import load_tokens

def contact_view(page: ft.Page, go):
    access, _ = load_tokens()

    name    = ft.TextField(label='Full Name *', prefix_icon=ft.Icons.PERSON)
    email   = ft.TextField(label='Email *', prefix_icon=ft.Icons.EMAIL)
    subject = ft.TextField(label='Subject *', prefix_icon=ft.Icons.SUBJECT)
    message = ft.TextField(label='Message *', multiline=True, min_lines=4)
    error   = ft.Text('', color=ft.Colors.RED_600, size=13)
    success = ft.Text('', color=ft.Colors.GREEN_600, size=13)
    loading = ft.ProgressRing(visible=False, width=20, height=20)

    # Prefill if logged in
    if access:
        status, user = get_user()
        if status == 200:
            name.value  = user.get('first_name', '') + ' ' + user.get('last_name', '')
            name.value  = name.value.strip() or user.get('username', '')
            email.value = user.get('email', '')

    def do_send(e):
        error.value   = ''
        success.value = ''

        if not all([name.value, email.value, subject.value, message.value]):
            error.value = 'Please fill in all fields.'
            page.update()
            return

        loading.visible = True
        page.update()

        status, resp = send_contact({
            'name':    name.value.strip(),
            'email':   email.value.strip(),
            'subject': subject.value.strip(),
            'message': message.value.strip(),
        })

        loading.visible = False

        if status == 201:
            success.value   = "Message sent! We'll get back to you soon."
            subject.value   = ''
            message.value   = ''
        else:
            error.value = str(resp)

        page.update()

    return ft.Column([
        # Info panel
        ft.Container(
            content=ft.Column([
                ft.Text('Get in Touch', size=18, weight=ft.FontWeight.BOLD, color='white'),
                ft.Text('Have a question? Reach out and we will get back to you.',
                        size=13, color='#cdc8bf'),
                ft.Divider(height=16, color='transparent'),
                _info_row(ft.Icons.LOCATION_ON, 'Student Affairs Office, UoM'),
                _info_row(ft.Icons.PHONE, '(+230) 12345678'),
                _info_row(ft.Icons.EMAIL, 'UniFind@uom.ac.mu'),
                _info_row(ft.Icons.ACCESS_TIME, 'Mon – Fri, 9:00am – 4:00pm'),
            ], spacing=12),
            padding=24,
            bgcolor='#5c4f3a',
            border_radius=12,
        ),

        # Form
        ft.Container(
            content=ft.Column([
                ft.Text('Send us a message', size=16, weight=ft.FontWeight.W_600, color='#2c2c2a'),
                name, email, subject, message,
                error, success,
                ft.Row([
                    loading,
                    ft.ElevatedButton('Send Message', bgcolor='#5c4f3a', color='white',
                                      on_click=do_send, icon=ft.Icons.SEND),
                ]),
            ], spacing=12),
            padding=24,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),
    ], spacing=16, scroll=ft.ScrollMode.AUTO)


def _info_row(icon, text):
    return ft.Row([
        ft.Icon(icon, color='white', size=16),
        ft.Text(text, size=13, color='#e8e4de'),
    ], spacing=10)