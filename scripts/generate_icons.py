import os
from PIL import Image, ImageDraw

def create_icon(size):
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer circle (Dark indigo background)
    margin = int(size * 0.06)
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=(26, 27, 38, 255),  # Dark navy/slate
        outline=(99, 102, 241, 255),  # Indigo accent
        width=max(1, int(size * 0.05))
    )
    
    # Focus target / Shield core
    center = size / 2.0
    r1 = size * 0.30
    draw.ellipse(
        [center - r1, center - r1, center + r1, center + r1],
        outline=(239, 68, 68, 255),  # Vibrant red focus ring
        width=max(1, int(size * 0.06))
    )
    
    # Center dot
    r2 = size * 0.12
    draw.ellipse(
        [center - r2, center - r2, center + r2, center + r2],
        fill=(239, 68, 68, 255)
    )
    
    return img

os.makedirs('/Users/macbookm4pro/.gemini/antigravity/scratch/focus-saver/icons', exist_ok=True)
for s in [16, 32, 48, 128]:
    icon = create_icon(s)
    icon.save(f'/Users/macbookm4pro/.gemini/antigravity/scratch/focus-saver/icons/icon{s}.png')
print("Icons generated successfully!")
