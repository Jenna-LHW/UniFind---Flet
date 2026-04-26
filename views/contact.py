import flet as ft
from api import send_contact

BROWN = '#5c4f3a'

def contact_view(page: ft.Page, go):
    page.title = 'Contact Us'

    def _field(label, icon, multiline=False, min_lines=1, max_lines=1):
        return ft.TextField(
            label=label, prefix_icon=icon, multiline=multiline,
            min_lines=min_lines, max_lines=max_lines,
            border_radius=12, filled=True, bgcolor='white',
            border_color='#d6d1c8', focused_border_color=BROWN,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )

    name_f    = _field('Your Name', ft.Icons.PERSON_OUTLINE)
    email_f   = _field('Your Email', ft.Icons.EMAIL_OUTLINED)
    subject_f = _field('Subject', ft.Icons.SUBJECT_ROUNDED)
    message_f = _field('Message', ft.Icons.MESSAGE_OUTLINED,
                        multiline=True, min_lines=4, max_lines=6)
    error   = ft.Text('', color=ft.Colors.RED_600, size=13)
    success = ft.Text('', color=ft.Colors.GREEN_600, size=13)
    loading = ft.ProgressRing(visible=False, width=22, height=22, color=BROWN)

    def do_send(e):
        error.value = ''; success.value = ''
        if not all([name_f.value, email_f.value, subject_f.value, message_f.value]):
            error.value = 'Please fill in all fields.'; page.update(); return
        loading.visible = True; page.update()
        s, resp = send_contact({
            'name': name_f.value.strip(), 'email': email_f.value.strip(),
            'subject': subject_f.value.strip(), 'message': message_f.value.strip(),
        })
        loading.visible = False
        if s in (200, 201):
            success.value = 'Message sent successfully!'
            for f in [name_f, email_f, subject_f, message_f]:
                f.value = ''
        else:
            error.value = 'Failed to send message. Please try again.'
        page.update()

    def _contact_row(icon, label, value):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color='white', size=18),
                    width=40, height=40, bgcolor=BROWN, border_radius=12,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(label, size=11, color='#9a8f80'),
                    ft.Text(value, size=13, color='#2c2c2a', weight=ft.FontWeight.W_500),
                ], spacing=1, expand=True),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            bgcolor='white', border_radius=14,
            border=ft.border.all(1, '#e8e2da'),
        )

    return ft.Column([

        # Contact info cards
        ft.Text('Get in Touch', size=14, weight=ft.FontWeight.W_600, color='#2c2c2a'),
        _contact_row(ft.Icons.EMAIL_OUTLINED,    'Email',   'unifind@uom.ac.mu'),
        _contact_row(ft.Icons.LOCATION_ON_OUTLINED, 'Location', 'University of Mauritius, Réduit'),
        _contact_row(ft.Icons.ACCESS_TIME_ROUNDED,  'Hours',  'Mon–Fri, 9am – 5pm'),

        # Message form
        ft.Container(
            content=ft.Column([
                ft.Text('Send a Message', size=14, weight=ft.FontWeight.W_600, color='#2c2c2a'),
                name_f, email_f, subject_f, message_f,
                error, success,
                ft.Row([
                    loading,
                    ft.ElevatedButton(
                        'Send Message',
                        bgcolor=BROWN, color='white', icon=ft.Icons.SEND_ROUNDED,
                        height=50, expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
                        on_click=do_send,
                    ),
                ], spacing=10),
            ], spacing=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=20),
            bgcolor='white', border_radius=16,
            border=ft.border.all(1, '#e8e2da'),
        ),

        ft.Container(height=8),

    ], spacing=12, scroll=ft.ScrollMode.AUTO)