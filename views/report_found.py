import flet as ft
from api import report_found_item
from storage import load_tokens

CATEGORIES = [('electronics','Electronics'),('clothing','Clothing'),('accessories','Accessories'),
              ('books_stationery','Books & Stationery'),('id_cards','ID & Cards'),
              ('bags','Bags'),('keys','Keys'),('other','Other')]

def report_found_view(page: ft.Page, go):
    access, _ = load_tokens()
    if not access:
        go('login')
        return ft.Text('')

    item_name   = ft.TextField(label='Item Name *', prefix_icon=ft.Icons.LABEL)
    category    = ft.Dropdown(
                    label='Category *',
                    options=[ft.dropdown.Option(k, v) for k, v in CATEGORIES],
                  )
    description = ft.TextField(
                    label='Description *',
                    multiline=True,
                    min_lines=3,
                    max_lines=5,
                  )
    found_at    = ft.TextField(
                    label='Found At Location *',
                    prefix_icon=ft.Icons.LOCATION_ON,
                  )
    date_found  = ft.TextField(
                    label='Date Found * (YYYY-MM-DD)',
                    prefix_icon=ft.Icons.CALENDAR_TODAY,
                  )
    photo_path  = ft.TextField(
                    label='Photo path (optional)',
                    prefix_icon=ft.Icons.IMAGE,
                    hint_text='e.g. /home/user/photo.jpg',
                  )
    error       = ft.Text('', color=ft.Colors.RED_600, size=13)
    success     = ft.Text('', color=ft.Colors.GREEN_600, size=13)
    loading     = ft.ProgressRing(visible=False, width=20, height=20)

    def do_submit(e):
        error.value   = ''
        success.value = ''

        if not all([item_name.value, category.value, description.value,
                    found_at.value, date_found.value]):
            error.value = 'Please fill in all required fields.'
            page.update()
            return

        loading.visible = True
        page.update()

        data = {
            'item_name':   item_name.value.strip(),
            'category':    category.value,
            'description': description.value.strip(),
            'found_at':    found_at.value.strip(),
            'date_found':  date_found.value.strip(),
        }

        photo = photo_path.value.strip() if photo_path.value else None
        status, resp = report_found_item(data, photo_path=photo)
        loading.visible = False

        if status == 201:
            success.value     = 'Found item reported successfully!'
            item_name.value   = ''
            description.value = ''
            found_at.value    = ''
            date_found.value  = ''
            category.value    = None
            photo_path.value  = ''
        else:
            error.value = str(resp)

        page.update()

    return ft.Column([

        # Header
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INVENTORY_2, color='#3b5c38'),
                ft.Text('Report a Found Item', size=18,
                        weight=ft.FontWeight.BOLD, color='#2c2c2a'),
            ], spacing=10),
            padding=20,
            bgcolor='white',
            border_radius=12,
            border=ft.border.all(1, '#d6d1c8'),
        ),

        # Form
        ft.Container(
            content=ft.Column([

                # Item details section
                ft.Text('Item Details', size=14,
                        weight=ft.FontWeight.W_600, color='#3b5c38'),
                item_name,
                category,
                description,

                ft.Divider(height=8, color='transparent'),

                # Location & date section
                ft.Text('Location & Date', size=14,
                        weight=ft.FontWeight.W_600, color='#3b5c38'),
                found_at,
                date_found,

                ft.Divider(height=8, color='transparent'),

                # Photo section
                ft.Text('Photo (optional)', size=14,
                        weight=ft.FontWeight.W_600, color='#3b5c38'),
                ft.Text(
                    'Enter the full path to your photo file.',
                    size=12,
                    color='#7a7670',
                ),
                photo_path,

                ft.Divider(height=8, color='transparent'),

                error,
                success,

                # Action buttons
                ft.Row([
                    loading,
                    ft.ElevatedButton(
                        'Submit Report',
                        bgcolor='#3b5c38',
                        color='white',
                        on_click=do_submit,
                        icon=ft.Icons.SEND,
                    ),
                    ft.TextButton(
                        'Cancel',
                        on_click=lambda e: go('home'),
                    ),
                ]),

            ], spacing=12),
            padding=24,
            bgcolor='white',
            border_radius=12,
            border=ft.border.all(1, '#d6d1c8'),
        ),

    ], spacing=16, scroll=ft.ScrollMode.AUTO)