import flet as ft
from api import get_reviews, post_review, like_review
from storage import load_tokens

BROWN      = '#5c4f3a'
CARD_BG    = 'white'
BORDER_CLR = '#d6d1c8'
MUTED      = '#7a7670'
DARK       = '#2c2c2a'
GOLD       = '#e4a600'


def reviews_view(page: ft.Page, go):
    access, _ = load_tokens()
    is_auth   = bool(access)

    status, data = get_reviews()
    reviews = data if isinstance(data, list) else data.get('results', [])

    total      = len(reviews)
    avg_rating = round(sum(r.get('rating', 0) for r in reviews) / total, 1) if total else 0
    rating_counts = {i: sum(1 for r in reviews if r.get('rating') == i) for i in range(1, 6)}

    rating_state = {'value': 0}
    comment    = ft.TextField(label='Your Review', multiline=True, min_lines=3,
                              border_color=BORDER_CLR)
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
                    icon_color=GOLD,
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
            success.value = 'Review submitted! Reload the page to see it.'
            comment.value = ''
            set_rating(0)
        else:
            if isinstance(resp, dict):
                msgs = [f"{v[0] if isinstance(v, list) else v}" for v in resp.values()]
                error.value = '\n'.join(msgs)
            else:
                error.value = str(resp)
        page.update()

    # ── Rating breakdown bar ────────────────────────────────
    def rating_bar(star_val, count):
        pct = (count / total) if total else 0
        return ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.STAR, color=GOLD, size=12),
                ft.Text(str(star_val), size=12, color=MUTED, width=8),
            ], spacing=3),
            ft.Container(
                content=ft.Container(
                    width=max(2, 140 * pct),
                    height=8,
                    bgcolor=GOLD,
                    border_radius=4,
                ),
                width=140, height=8,
                bgcolor='#f0ece6',
                border_radius=4,
            ),
            ft.Text(str(count), size=12, color=MUTED, width=20),
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # ── Review card with like button ───────────────────────
    def review_card(r):
        review_id   = r.get('id')
        like_count  = r.get('total_likes', 0)
        liked_state = {'liked': False}

        like_count_text = ft.Text(str(like_count), size=12, color=MUTED)

        like_btn = ft.IconButton(
            icon=ft.Icons.THUMB_UP_OUTLINED,
            icon_color=MUTED,
            icon_size=16,
            tooltip='Like this review' if is_auth else 'Log in to like',
        )

        def on_like(e):
            if not is_auth:
                go('login')
                return
            s, resp = like_review(review_id)
            if s == 200:
                liked_state['liked'] = resp.get('liked', not liked_state['liked'])
                like_count_text.value = str(resp.get('total_likes', like_count))
                like_btn.icon_color = BROWN if liked_state['liked'] else MUTED
                like_btn.icon = ft.Icons.THUMB_UP if liked_state['liked'] else ft.Icons.THUMB_UP_OUTLINED
                page.update()

        like_btn.on_click = on_like

        stars = ft.Row([
            ft.Icon(ft.Icons.STAR if i <= r.get('rating', 0) else ft.Icons.STAR_BORDER,
                    color=GOLD, size=14)
            for i in range(1, 6)
        ], spacing=2)

        reply = r.get('reply')
        reply_box = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SHIELD, color=BROWN, size=14),
                    ft.Text('UniFind Team', size=12, weight=ft.FontWeight.W_600, color=BROWN),
                ], spacing=6),
                ft.Text(reply.get('comment', '') if reply else '', size=13, color='#3d3d3a'),
            ], spacing=4),
            padding=12,
            bgcolor='#f5f2ee',
            border_radius=ft.BorderRadius.only(top_right=8, bottom_left=8, bottom_right=8),
            border=ft.Border.only(left=ft.BorderSide(3, BROWN)),
            margin=ft.Margin.only(top=8),
            visible=bool(reply),
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(str(r.get('username', '?'))[0].upper(),
                                        color='white', size=14, weight=ft.FontWeight.BOLD),
                        width=36, height=36, bgcolor=BROWN,
                        border_radius=18, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(str(r.get('username', '')), size=13, weight=ft.FontWeight.W_600),
                        stars,
                    ], spacing=2, expand=True),
                    ft.Text(str(r.get('created_at', ''))[:10], size=11, color=MUTED),
                ], spacing=10),
                ft.Text(r.get('comment', ''), size=13, color='#3d3d3a'),
                reply_box,
                ft.Row([
                    like_btn,
                    like_count_text,
                ], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=8),
            padding=16,
            bgcolor=CARD_BG,
            border_radius=12,
            border=ft.Border.all(1, BORDER_CLR),
        )

    # ── Write / login section ──────────────────────────────
    write_section = ft.Container(
        content=ft.Column([
            ft.Text('Write a Review', size=14, weight=ft.FontWeight.W_600, color=BROWN),
            star_row,
            comment,
            error, success,
            ft.ElevatedButton('Submit Review', bgcolor=BROWN, color='white',
                              on_click=do_submit, icon=ft.Icons.SEND),
        ], spacing=10),
        padding=20,
        bgcolor=CARD_BG,
        border_radius=12,
        border=ft.Border.all(1, BORDER_CLR),
        visible=is_auth,
    )

    login_prompt = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.LOCK, color=BROWN),
            ft.Text('Please ', size=13),
            ft.TextButton('log in', on_click=lambda e: go('login')),
            ft.Text(' to write a review.', size=13),
        ]),
        padding=16,
        bgcolor=CARD_BG,
        border_radius=12,
        border=ft.Border.all(1, BORDER_CLR),
        visible=not is_auth,
    )

    # ── Stats header ───────────────────────────────────────
    stats_header = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text(str(avg_rating), size=40, weight=ft.FontWeight.BOLD, color=DARK),
                ft.Row([
                    ft.Icon(ft.Icons.STAR if i <= round(avg_rating) else ft.Icons.STAR_BORDER,
                            color=GOLD, size=16)
                    for i in range(1, 6)
                ], spacing=2),
                ft.Text(f'{total} review{"s" if total != 1 else ""}', size=12, color=MUTED),
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.VerticalDivider(width=1, color=BORDER_CLR),
            ft.Column([
                rating_bar(5, rating_counts[5]),
                rating_bar(4, rating_counts[4]),
                rating_bar(3, rating_counts[3]),
                rating_bar(2, rating_counts[2]),
                rating_bar(1, rating_counts[1]),
            ], spacing=4, expand=True),
        ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        bgcolor=CARD_BG,
        border_radius=12,
        border=ft.Border.all(1, BORDER_CLR),
    )

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.STAR, color=GOLD),
                ft.Text('Community Reviews', size=18, weight=ft.FontWeight.BOLD, color=DARK),
            ], spacing=12),
            padding=ft.Padding.only(bottom=4),
        ),
        stats_header,
        write_section,
        login_prompt,
        ft.Text('All Reviews', size=16, weight=ft.FontWeight.W_600, color=DARK),
        *([review_card(r) for r in reviews] if reviews else
          [ft.Text('No reviews yet.', color=MUTED, italic=True)]),
    ], spacing=16, scroll=ft.ScrollMode.AUTO)
