#!/usr/bin/env python3
"""
压缩小程序图片到 200KB 以下
"""

from PIL import Image
import os

def compress_image(input_path, output_path, max_size_kb=200):
    """压缩图片到指定大小以下"""
    img = Image.open(input_path)

    # 如果是 RGBA 模式，转换为 RGB
    if img.mode == 'RGBA':
        # 创建白色背景
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # 使用 alpha 通道作为 mask
        img = background

    # 获取原始尺寸
    original_size = os.path.getsize(input_path) / 1024  # KB
    print(f"原始文件: {input_path}")
    print(f"原始大小: {original_size:.2f} KB")
    print(f"原始尺寸: {img.size}")

    # 如果已经小于目标大小，直接复制
    if original_size <= max_size_kb:
        img.save(output_path, 'JPEG', quality=85, optimize=True)
        print(f"✅ 文件已小于 {max_size_kb}KB，无需压缩")
        return

    # 逐步降低质量和尺寸
    quality = 85
    scale = 1.0

    while True:
        # 调整尺寸
        if scale < 1.0:
            new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
        else:
            resized_img = img

        # 保存到临时文件
        temp_path = output_path + '.tmp'
        resized_img.save(temp_path, 'JPEG', quality=quality, optimize=True)

        # 检查文件大小
        current_size = os.path.getsize(temp_path) / 1024  # KB

        if current_size <= max_size_kb:
            # 达到目标，重命名为最终文件
            os.rename(temp_path, output_path)
            print(f"✅ 压缩成功!")
            print(f"新文件大小: {current_size:.2f} KB")
            print(f"新文件尺寸: {resized_img.size}")
            print(f"压缩率: {(1 - current_size/original_size)*100:.1f}%")
            break

        # 继续压缩
        os.remove(temp_path)

        if quality > 60:
            quality -= 5
        elif scale > 0.5:
            scale -= 0.1
            quality = 85  # 重置质量
        else:
            # 无法压缩到目标大小
            print(f"⚠️  警告: 无法压缩到 {max_size_kb}KB 以下")
            print(f"当前大小: {current_size:.2f} KB")
            resized_img.save(output_path, 'JPEG', quality=quality, optimize=True)
            break

if __name__ == '__main__':
    # 压缩 logo.png
    input_file = 'miniprogram/images/logo.png'
    output_file = 'miniprogram/images/logo.jpg'

    compress_image(input_file, output_file, max_size_kb=200)

    print("\n📝 注意: 图片已转换为 JPG 格式")
    print("请在代码中将 logo.png 的引用改为 logo.jpg")
