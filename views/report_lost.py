import flet as ft
from api import report_lost_item
from storage import load_tokens

CATEGORIES = [('electronics','Electronics'),('clothing','Clothing'),('accessories','Accessories'),
              ('books_stationery','Books & Stationery'),('id_cards','ID & Cards'),
              ('bags','Bags'),('keys','Keys'),('other','Other')]
BROWN = '#5c4f3a'

def _field(label, icon, multiline=False, min_lines=1, max_lines=1, hint=None):
    return ft.TextField(
        label=label,
        prefix_icon=icon,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines,
        hint_text=hint,
        border_radius=12,
        filled=True,
        bgcolor='white',
        border_color='#d6d1c8',
        focused_border_color=BROWN,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )

def report_lost_view(page: ft.Page, go):
    access, _ = load_tokens()
    if not access:
        go('login')
        return ft.Text('')

    item_name   = _field('Item Name *', ft.Icons.LABEL_OUTLINE)
    category    = ft.Dropdown(
        label='Category *',
        options=[ft.dropdown.Option(k, v) for k, v in CATEGORIES],
        border_radius=12,
        filled=True,
        bgcolor='white',
        border_color='#d6d1c8',
        focused_border_color=BROWN,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
    )
    description = _field('Description *', ft.Icons.NOTES_ROUNDED,
                          multiline=True, min_lines=3, max_lines=5)
    last_seen   = _field('Last Seen Location *', ft.Icons.LOCATION_ON_OUTLINED)
    date_lost   = _field('Date Lost * (YYYY-MM-DD)', ft.Icons.CALENDAR_TODAY_OUTLINED)
    photo_path  = _field('Photo path (optional)', ft.Icons.IMAGE_OUTLINED,
                          hint='/home/user/photo.jpg')
    error   = ft.Text('', color=ft.Colors.RED_600, size=13)
    success = ft.Text('', color=ft.Colors.GREEN_600, size=13)
    loading = ft.ProgressRing(visible=False, width=22, height=22, color=BROWN)

    def do_submit(e):
        error.value = ''; success.value = ''
        if not all([item_name.value, category.value, description.value,
                    last_seen.value, date_lost.value]):
            error.value = 'Please fill in all required fields.'
            page.update(); return

        loading.visible = True; page.update()
        data = {
            'item_name': item_name.value.strip(), 'category': category.value,
            'description': description.value.strip(), 'last_seen': last_seen.value.strip(),
            'date_lost': date_lost.value.strip(),
        }
        photo = photo_path.value.strip() if photo_path.value else None
        status, resp = report_lost_item(data, photo_path=photo)
        loading.visible = False

        if status == 201:
            success.value = 'Lost item reported successfully!'
            for f in [item_name, description, last_seen, date_lost, photo_path]:
                f.value = ''
            category.value = None
        else:
            error.value = str(resp)
        page.update()

    def _section(label):
        return ft.Text(label, size=12, weight=ft.FontWeight.W_600,
                       color='#9a8f80', style=ft.TextStyle(letter_spacing=0.8))

    return ft.Column([

        ft.Container(
            content=ft.Column([
                _section('ITEM DETAILS'),
                item_name,
                category,
                description,
                ft.Container(height=4),
                _section('LOCATION & DATE'),
                last_seen,
                date_lost,
                ft.Container(height=4),
                _section('PHOTO (OPTIONAL)'),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color='#9a8f80'),
                        ft.Text('Enter the full file path to your photo.',
                                size=11, color='#9a8f80'),
                    ], spacing=6),
                ),
                photo_path,
                ft.Container(height=4),
                error,
                success,
                ft.Row([
                    loading,
                    ft.ElevatedButton(
                        'Submit Report',
                        bgcolor=BROWN, color='white',
                        icon=ft.Icons.SEND_ROUNDED,
                        height=50, expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
                        on_click=do_submit,
                    ),
                ], spacing=10),
                ft.TextButton(
                    'Cancel',
                    on_click=lambda e: go('home'),
                    style=ft.ButtonStyle(color='#9a8f80'),
                ),
            ], spacing=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=24),
            bgcolor='white',
            border_radius=20,
            border=ft.border.all(1, '#e8e2da'),
        ),

    ], spacing=0, scroll=ft.ScrollMode.AUTO)
