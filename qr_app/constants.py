from __future__ import annotations


AVATAR_MAP = {
    "Boy": "avatars/boy.png",
    "Boy 2": "avatars/boy_2.png",
    "Cat": "avatars/cat.png",
    "Data Analyst": "avatars/data_analyst.png",
    "Developer": "avatars/developer.png",
    "Doctor": "avatars/doctor.png",
    "Girl": "avatars/girl.png",
    "Girl 1": "avatars/girl_1.png",
    "Girl 3": "avatars/girl_3.png",
    "Kid": "avatars/kid.png",
    "Kid Girl": "avatars/kid_girl.png",
    "Man": "avatars/man.png",
    "Man 2": "avatars/man_2.png",
    "Ninja": "avatars/ninja.png",
    "Panda": "avatars/panda.png",
    "Small Boy": "avatars/small_boy.png",
    "Wizard": "avatars/wizard.png",
    "Women": "avatars/women.png",
}

COLOR_PALETTE = [
    ("Black", "#000000"),
    ("White", "#FFFFFF"),
    ("Red", "#FF0000"),
    ("Green", "#008000"),
    ("Blue", "#0000FF"),
    ("Purple", "#800080"),
    ("Yellow", "#FFFF00"),
    ("Orange", "#FFA500"),
    ("Pink", "#FFC0CB"),
    ("Light Blue", "#ADD8E6"),
    ("Light Green", "#90EE90"),
    ("Gold", "#FFD700"),
    ("Crimson", "#DC143C"),
    ("Hot Pink", "#FF1493"),
    ("Lime", "#7FFF00"),
    ("Orange Red", "#FF4500"),
    ("Sea Green", "#2E8B57"),
]

PALETTE_NAMES = [item[0] for item in COLOR_PALETTE]
PALETTE_HEX = [item[1] for item in COLOR_PALETTE]
PALETTE_DISPLAY = [f"{name} ({hex_value})" for name, hex_value in COLOR_PALETTE]
