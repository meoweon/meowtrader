"""
创建 MeowTrader 图标文件

使用 Pillow 生成一个专业的图标文件（包含多种尺寸）

依赖: Pillow (PIL)
安装: pip install Pillow 或 uv add Pillow

用法:
    python scripts/create_icon.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
ICON_PATH = PROJECT_ROOT / "resources" / "icon.ico"

# 创建 resources 目录
ICON_PATH.parent.mkdir(exist_ok=True)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("错误: 需要安装 Pillow 库")
    print("请运行: pip install Pillow")
    print("或者: uv add Pillow")
    sys.exit(1)

# 定义图标尺寸（Windows ICO 文件需要多种尺寸）
SIZES = [16, 32, 48, 64, 128, 256]

# 创建图标图像列表
images = []

for size in SIZES:
    # 创建图像（带透明通道）
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变背景（深蓝到浅蓝）
    # 简化：使用纯色背景，深蓝色系
    bg_color = (30, 60, 120, 255)  # 深蓝色 RGB
    draw.rectangle([0, 0, size, size], fill=bg_color)
    
    # 绘制圆形边框（白色）
    border_width = max(1, size // 32)
    margin = border_width * 2
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        outline=(255, 255, 255, 255),
        width=border_width
    )
    
    # 绘制 "M" 字母（MeowTrader）
    font_size = int(size * 0.6)
    
    # 尝试加载字体
    font = None
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            continue
    
    if font is None:
        # 使用默认字体
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # 计算文本位置（居中）
    text = "M"
    if font:
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # 如果 textbbox 不可用，使用旧方法
            try:
                text_width, text_height = draw.textsize(text, font=font)
            except:
                text_width = size * 0.6
                text_height = size * 0.6
    else:
        text_width = size * 0.6
        text_height = size * 0.6
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - int(size * 0.05)  # 稍微上移，视觉上更居中
    
    # 绘制文本（白色，加粗效果）
    if font:
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    else:
        draw.text((x, y), text, fill=(255, 255, 255, 255))
    
    # 转换为适合 ICO 的格式
    # ICO 格式支持 RGBA，但某些工具可能不支持，所以为小图标保留透明，大图标使用白色背景
    if size <= 32:
        # 小图标保持透明背景
        images.append(img)
    else:
        # 大图标使用白色背景（更好的兼容性）
        rgb_img = Image.new('RGB', (size, size), (255, 255, 255))
        if img.mode == 'RGBA':
            rgb_img.paste(img, mask=img.split()[3])  # 使用 alpha 通道作为 mask
        else:
            rgb_img.paste(img)
        images.append(rgb_img)

# 保存为 ICO 文件
try:
    # 使用第一个图像保存，并指定所有尺寸
    images[0].save(
        ICON_PATH,
        format='ICO',
        sizes=[(img.width, img.height) for img in images]
    )
    
    file_size = ICON_PATH.stat().st_size
    print(f"✓ 图标已创建: {ICON_PATH}")
    print(f"  包含尺寸: {', '.join(f'{s}x{s}' for s in SIZES)}")
    print(f"  文件大小: {file_size / 1024:.1f} KB")
    print()
    print("提示: 如果需要更专业的图标，可以使用在线工具或设计软件创建，")
    print("      然后替换 resources/icon.ico 文件")
except Exception as e:
    print(f"错误: 无法保存图标文件: {e}")
    sys.exit(1)
