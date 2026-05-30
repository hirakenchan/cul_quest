from PIL import Image


INPUT_FILE = "gorem_original.png"
OUTPUT_FILE = "gorem.png"

# 元画像を開く
img = Image.open(INPUT_FILE).convert("RGBA")

# 黒背景を除いて、キャラ部分だけ切り抜く
pixels = img.load()
width, height = img.size

min_x, min_y = width, height
max_x, max_y = 0, 0

for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]

        # ほぼ黒以外をキャラとして判定
        if a > 0 and not (r < 15 and g < 15 and b < 15):
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

cropped = img.crop((min_x, min_y, max_x + 1, max_y + 1))

# 正方形のキャンバスに中央配置
size = max(cropped.size)
square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
square.paste(
    cropped,
    ((size - cropped.width) // 2, (size - cropped.height) // 2),
)

# ゲーム用サイズに縮小
sprite = square.resize((46, 46), Image.Resampling.NEAREST)

# ほぼ黒を透明にする
data = []
for r, g, b, a in sprite.getdata():
    if r < 15 and g < 15 and b < 15:
        data.append((0, 0, 0, 0))
    else:
        data.append((r, g, b, a))

sprite.putdata(data)
sprite.save(OUTPUT_FILE)

print(f"{OUTPUT_FILE} を作成しました")