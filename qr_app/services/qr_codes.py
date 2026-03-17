from __future__ import annotations

from io import BytesIO

import qrcode
import streamlit as st
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, GappedSquareModuleDrawer, SquareModuleDrawer

from qr_app.db import get_db_connection, rows_to_dicts
from qr_app.state import clear_qr_preview_state


@st.cache_data(ttl=3600)
def generate_qr_image(
    data: str,
    fg_color: str,
    bg_color: str,
    box_size: int = 10,
    border: int = 4,
    style: str = "square",
) -> bytes:
    drawer_map = {
        "square": SquareModuleDrawer(),
        "gapped": GappedSquareModuleDrawer(),
        "circle": CircleModuleDrawer(),
    }
    drawer = drawer_map.get(style, SquareModuleDrawer())
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=SolidFillColorMask(
            front_color=tuple(int(fg_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)),
            back_color=tuple(int(bg_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)),
        ),
    )
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def save_qr_record(
    user_id: int,
    qr_text: str,
    fg_color_name: str,
    bg_color_name: str,
    qr_style: str,
    box_size: int,
    border: int,
) -> None:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO qr_codes (
                user_id,
                qr_text,
                fg_color_name,
                bg_color_name,
                qr_style,
                box_size,
                border
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, qr_text, fg_color_name, bg_color_name, qr_style, box_size, border),
        )
        connection.commit()

    load_user_qrs.clear()


@st.cache_data(ttl=60)
def load_user_qrs(user_id: int) -> list[dict]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM qr_codes
            WHERE user_id = ?
              AND deleted_at IS NULL
            ORDER BY datetime(created_at) DESC, id DESC
            """,
            (user_id,),
        )
        return rows_to_dicts(cursor.fetchall())


def delete_qr(qr_id: int, user_id: int) -> tuple[bool, str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE qr_codes
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ? AND deleted_at IS NULL
            """,
            (qr_id, user_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Unable to delete that QR code."

    load_user_qrs.clear()
    clear_qr_preview_state(user_id)
    return True, "QR deleted successfully."


def clear_all_qrs(user_id: int) -> tuple[bool, str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE qr_codes
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND deleted_at IS NULL
            """,
            (user_id,),
        )
        connection.commit()

    load_user_qrs.clear()
    clear_qr_preview_state(user_id)
    return True, "All QR history cleared."
