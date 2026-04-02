import flet as ft
from api import report_lost_item
from storage import load_tokens

CATEGORIES = [('electronics','Electronics'),('clothing','Clothing'),('accessories','Accessories'),
              ('books_stationery','Books & Stationery'),('id_cards','ID & Cards'),
              ('bags','Bags'),('keys','Keys'),('other','Other')]

def report_lost_view(page: ft.Page, go):
    access, _ = load_tokens()
    if not access:
        go('login')
        return ft.Text('')

    item_name   = ft.TextField(label='Item Name *', prefix_icon=ft.Icons.LABEL)
    category    = ft.Dropdown(label='Category *',
                    options=[ft.dropdown.Option(k, v) for k, v in CATEGORIES])
    description = ft.TextField(label='Description *', multiline=True, min_lines=3, max_lines=5)
    last_seen   = ft.TextField(label='Last Seen Location *', prefix_icon=ft.Icons.LOCATION_ON)
    date_lost   = ft.TextField(label='Date Lost * (YYYY-MM-DD)', prefix_icon=ft.Icons.CALENDAR_TODAY)
    error       = ft.Text('', color=ft.Colors.RED_600, size=13)
    success     = ft.Text('', color=ft.Colors.GREEN_600, size=13)
    loading     = ft.ProgressRing(visible=False, width=20, height=20)

    def do_submit(e):
        error.value   = ''
        success.value = ''

        if not all([item_name.value, category.value, description.value, last_seen.value, date_lost.value]):
            error.value = 'Please fill in all required fields.'
            page.update()
            return

        loading.visible = True
        page.update()

        data = {
            'item_name':   item_name.value.strip(),
            'category':    category.value,
            'description': description.value.strip(),
            'last_seen':   last_seen.value.strip(),
            'date_lost':   date_lost.value.strip(),
        }

        status, resp = report_lost_item(data)
        loading.visible = False

        if status == 201:
            success.value = 'Lost item reported successfully!'
            item_name.value = category.value = description.value = last_seen.value = date_lost.value = ''
        else:
            error.value = str(resp)

        page.update()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SEARCH, color='#5c4f3a'),
                ft.Text('Report a Lost Item', size=18, weight=ft.FontWeight.BOLD, color='#2c2c2a'),
            ], spacing=10),
            padding=20,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),
        ft.Container(
            content=ft.Column([
                ft.Text('Item Details', size=14, weight=ft.FontWeight.W_600, color='#5c4f3a'),
                item_name, category, description,
                ft.Divider(height=8, color='transparent'),
                ft.Text('Location & Date', size=14, weight=ft.FontWeight.W_600, color='#5c4f3a'),
                last_seen, date_lost,
                error, success,
                ft.Row([
                    loading,
                    ft.ElevatedButton('Submit Report', bgcolor='#5c4f3a', color='white',
                                      on_click=do_submit, icon=ft.Icons.SEND),
                    ft.TextButton('Cancel', on_click=lambda e: go('home')),
                ]),
            ], spacing=12),
            padding=24,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),
    ], spacing=16, scroll=ft.ScrollMode.AUTO)