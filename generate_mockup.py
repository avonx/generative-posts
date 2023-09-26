import re
from PIL import Image, ImageDraw, ImageFont
import unicodedata


def max_circular_crop(image):
    """
    画像から最大サイズの円形を切り出します。
    """
    size = min(image.size)
    offset = [(image.size[i] - size) // 2 for i in range(2)]
    cropped = image.crop(
        (offset[0], offset[1], offset[0] + size, offset[1] + size))

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    result = Image.composite(
        cropped, Image.new("RGBA", cropped.size, (0, 0, 0, 0)), mask
    )
    return result


def max_rectangular_crop(image, target_aspect_ratio):
    """
    画像から指定のアスペクト比で最大サイズの矩形を切り出します。
    """
    width, height = image.size
    image_aspect_ratio = width / height
    if image_aspect_ratio > target_aspect_ratio:
        new_width = int(height * target_aspect_ratio)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target_aspect_ratio)
        top = (height - new_height) // 2
        return image.crop((0, top, width, top + new_height))


def split_emoji_from_text(text):
    # 絵文字の正規表現
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "]+"
    )
    # テキストから絵文字を分離する
    emojis = emoji_pattern.findall(text)
    text_parts = emoji_pattern.split(text)
    return text_parts, emojis


def char_width(c):
    """文字の幅を返す。全角の場合は2、半角の場合は1を返す。"""
    if unicodedata.east_asian_width(c) in ("F", "W", "A"):
        return 2
    else:
        return 1


def wrap_text(text, font, max_width):
    lines = []
    current_line = ""
    current_width = 0

    for char in text:
        char_width_val = char_width(char) * font.getbbox("A")[2] / 2

        if current_width + char_width_val <= max_width / 1.5:
            current_line += char
            current_width += char_width_val
        else:
            lines.append(current_line)
            current_line = char
            current_width = char_width_val

    if current_line:
        lines.append(current_line)

    return lines


def draw_text(draw, position, text, font, emoji_font, max_width, fill=(255, 255, 255)):
    # テキスト全体に対してwrap_text関数を適用
    lines = wrap_text(text, font, max_width)
    y_text = position[1]

    for line in lines:
        x_text = position[0]
        for char in line:
            # 絵文字かどうかをチェック
            if ord(char) in range(0x1F600, 0x1FAFF):  # 絵文字のUnicode範囲
                char_font = emoji_font
            else:
                char_font = font

            draw.text((x_text, y_text), char, font=char_font, fill=fill)
            x_text += char_font.getbbox(char)[2]

        y_text += font.getbbox(line)[3]

    return y_text


def place_text(
    draw, textbox_position, textbox_size, text, font, emoji_font, fill=(
        255, 255, 255)
):
    # テキストボックスの境界線を描画 (必要であれば)
    # draw.rectangle([textbox_position, (textbox_position[0] + textbox_size[0], textbox_position[1] + textbox_size[1])], outline=(255,0,0))

    # テキストボックス内にテキストを配置
    draw_text(
        draw,
        textbox_position,
        text,
        font,
        emoji_font,
        max_width=textbox_size[0],
        fill=fill,
    )


# コレは絶対HTMLで描画する仕様にしておいたほうがよかった。。。
def generate_instagram_mockup(
    circle_image_path, rectangle_image_path, name, situation, comment
):
    template_image_path = "./templates/instagram_template.jpg"  # TODO ローカルパス

    # 座標とサイズの変数
    circle_position = (265, 117)
    circle_size = (58, 58)
    rect_position = (248, 200)
    rect_size = (548, 540)

    # 画像を読み込む
    template_image = Image.open(template_image_path)
    circle_image = Image.open(circle_image_path)
    rectangle_image = Image.open(rectangle_image_path)

    # 画像を最大サイズで切り出す
    cropped_circle = max_circular_crop(circle_image)
    cropped_rectangle = max_rectangular_crop(
        rectangle_image, rect_size[0] / rect_size[1]
    )

    # テンプレートのサイズにリサイズ
    cropped_circle = cropped_circle.resize(circle_size, Image.LANCZOS)
    cropped_rectangle = cropped_rectangle.resize(rect_size, Image.LANCZOS)

    # 画像をテンプレートに貼り付ける
    template_image.paste(cropped_circle, circle_position, cropped_circle)
    template_image.paste(cropped_rectangle, rect_position)

    # テキストを配置する
    draw = ImageDraw.Draw(template_image)

    # フォントの読み込み
    font = ImageFont.truetype(
        "/Library/Fonts/Arial Unicode.ttf", 20)  # TODO ローカルパス
    emoji_font = ImageFont.truetype(
        "/System/Library/Fonts/Apple Color Emoji.ttc", 20
    )  # TODO ローカルパス

    # 名前を描画
    place_text(draw, (345, 122), (300, 35), name,
               font, emoji_font, fill=(20, 20, 20))

    # situationを描画
    place_text(
        draw, (345, 145), (300, 35), situation, font, emoji_font, fill=(180, 180, 180)
    )

    # コメントを描画
    place_text(
        draw, (280, 850), (500, 120), comment, font, emoji_font, fill=(20, 20, 20)
    )

    return template_image


if __name__ == "__main__":
    # 画像を読み込む
    circle_image_path = "./input/reference_2.png"
    rectangle_image_path = "./input/target.png"

    name = "橋本環奈"
    situation = "お寺で、デジタルデトックス"
    comment = """お寺で疲れを癒してきました！🚀座禅ってあんなにスッキルするんだね〜お勧めしてくれた方に感謝！🚀 #座禅"""

    generated_mockup = generate_instagram_mockup(
        circle_image_path, rectangle_image_path, name, situation, comment
    )

    # 結果を保存する
    generated_mockup.save("test.jpg")
