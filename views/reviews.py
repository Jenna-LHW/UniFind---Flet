import flet as ft
from api import get_reviews, post_review
from storage import load_tokens

def reviews_view(page: ft.Page, go):
    access, _ = load_tokens()
    is_auth   = bool(access)

    status, data = get_reviews()
    reviews = data if isinstance(data, list) else data.get('results', [])

    total      = len(reviews)
    avg_rating = round(sum(r.get('rating', 0) for r in reviews) / total, 1) if total else 0

    rating_state = {'value': 0}
    comment    = ft.TextField(label='Your Review', multiline=True, min_lines=3)
    error      = ft.Text('', color=ft.Colors.RED_600, size=13)
    success    = ft.Text('', color=ft.Colors.GREEN_600, size=13)
    star_row   = ft.Row(spacing=4)

    def set_rating(val):
        rating_state['value'] = val
        star_row.controls.clear()
        for i in range(1, 6):
            star_row.controls.append(
                ft.IconButton(
                    icon=ft.Icons.STAR if i <= val else ft.Icons.STAR_BORDER,
                    icon_color='#e4a600',
                    icon_size=28,
                    on_click=lambda e, v=i: set_rating(v),
                )
            )
        page.update()

    set_rating(0)

    def do_submit(e):
        error.value   = ''
        success.value = ''
        if not rating_state['value']:
            error.value = 'Please select a rating.'
            page.update()
            return
        if not comment.value.strip():
            error.value = 'Please write a review.'
            page.update()
            return

        s, resp = post_review({'rating': rating_state['value'], 'comment': comment.value.strip()})
        if s == 201:
            success.value = 'Review submitted!'
            comment.value = ''
            set_rating(0)
        else:
            error.value = str(resp)
        page.update()

    def review_card(r):
        stars = ft.Row([
            ft.Icon(ft.Icons.STAR if i <= r.get('rating', 0) else ft.Icons.STAR_BORDER,
                    color='#e4a600', size=14)
            for i in range(1, 6)
        ], spacing=2)

        reply = r.get('reply')
        reply_box = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SHIELD, color='#5c4f3a', size=14),
                    ft.Text('UniFind Team', size=12, weight=ft.FontWeight.W_600, color='#5c4f3a'),
                ], spacing=6),
                ft.Text(reply.get('comment', '') if reply else '', size=13, color='#3d3d3a'),
            ], spacing=4),
            padding=12,
            bgcolor='#f5f2ee',
            border_radius=ft.BorderRadius.only(top_right=8, bottom_left=8, bottom_right=8),
            border=ft.Border.only(left=ft.BorderSide(3, '#5c4f3a')),
            margin=ft.Margin.only(top=8),
            visible=bool(reply),
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(str(r.get('user', '?'))[0].upper(),
                                        color='white', size=14, weight=ft.FontWeight.BOLD),
                        width=36, height=36, bgcolor='#5c4f3a',
                        border_radius=18, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(str(r.get('user', '')), size=13, weight=ft.FontWeight.W_600),
                        stars,
                    ], spacing=2, expand=True),
                    ft.Text(str(r.get('created_at', ''))[:10], size=11, color='#7a7670'),
                ], spacing=10),
                ft.Text(r.get('comment', ''), size=13, color='#3d3d3a'),
                reply_box,
            ], spacing=8),
            padding=16,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        )

    write_section = ft.Container(
        content=ft.Column([
            ft.Text('Write a Review', size=14, weight=ft.FontWeight.W_600, color='#5c4f3a'),
            star_row,
            comment,
            error, success,
            ft.ElevatedButton('Submit Review', bgcolor='#5c4f3a', color='white',
                              on_click=do_submit, icon=ft.Icons.SEND),
        ], spacing=10),
        padding=20,
        bgcolor='white',
        border_radius=12,
        border=ft.Border.all(1, '#d6d1c8'),
        visible=is_auth,
    )

    login_prompt = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.LOCK, color='#5c4f3a'),
            ft.Text('Please ', size=13),
            ft.TextButton('log in', on_click=lambda e: go('login')),
            ft.Text(' to write a review.', size=13),
        ]),
        padding=16,
        bgcolor='white',
        border_radius=12,
        border=ft.Border.all(1, '#d6d1c8'),
        visible=not is_auth,
    )

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.STAR, color='#e4a600'),
                ft.Column([
                    ft.Text('Community Reviews', size=18, weight=ft.FontWeight.BOLD, color='#2c2c2a'),
                    ft.Text(f'{avg_rating}★ average from {total} review{"s" if total != 1 else ""}',
                            size=12, color='#7a7670'),
                ], spacing=2),
            ], spacing=12),
            padding=20,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),

        write_section,
        login_prompt,

        ft.Text('All Reviews', size=16, weight=ft.FontWeight.W_600, color='#2c2c2a'),
        *([review_card(r) for r in reviews] if reviews else
          [ft.Text('No reviews yet.', color='#7a7670')]),

    ], spacing=16, scroll=ft.ScrollMode.AUTO)