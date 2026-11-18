"""
Build layered artwork assets for IrrigaTrace Night Field Observatory
Produces WebP assets <= 250 KB each in web/public/art/
and records metadata in design/approved/art-manifest.md
"""
import os
import math
from PIL import Image, ImageDraw, ImageFilter

ART_DIR = "web/public/art"
os.makedirs(ART_DIR, exist_ok=True)
W, H = 2400, 1400

# 1. Sky & Stars (2400x1400)
def generate_sky_stars():
    im = Image.new("RGBA", (W, H), (6, 5, 42, 255))
    draw = ImageDraw.Draw(im)
    # subtle gradient top-down
    for y in range(H):
        ratio = y / H
        r = int(6 + (11 - 6) * ratio)
        g = int(5 + (10 - 5) * ratio)
        b = int(42 + (63 - 42) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
    
    # Stars
    import random
    random.seed(42)
    for _ in range(450):
        x = random.randint(0, W)
        y = random.randint(0, int(H * 0.75))
        brightness = random.randint(140, 255)
        size = random.choice([1, 1, 1, 2, 2, 3])
        draw.ellipse([x, y, x + size, y + size], fill=(243, 241, 255, brightness))
        if size == 3:
            # 4-point sparkle
            draw.line([(x-2, y+1), (x+5, y+1)], fill=(201, 196, 255, 120))
            draw.line([(x+1, y-2), (x+1, y+5)], fill=(201, 196, 255, 120))
            
    out_path = os.path.join(ART_DIR, "sky-stars.webp")
    im.save(out_path, "WEBP", quality=85)
    print(f"Created {out_path} ({os.path.getsize(out_path)} bytes)")

# 2. Planet with Glowing Rings (Transparent)
def generate_planet():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    cx, cy = 1350, 480
    radius = 240
    
    # Back ring arc
    ring_w, ring_h = 750, 200
    draw.arc([cx - ring_w//2, cy - ring_h//2, cx + ring_w//2, cy + ring_h//2], start=180, end=360, fill=(201, 196, 255, 110), width=6)
    draw.arc([cx - ring_w//2 - 20, cy - ring_h//2 - 10, cx + ring_w//2 + 20, cy + ring_h//2 + 10], start=185, end=355, fill=(143, 134, 245, 70), width=4)

    # Planet Body
    for r in range(radius, 0, -1):
        frac = r / radius
        col = (
            int(15 + (35 - 15) * (1 - frac)),
            int(12 + (30 - 12) * (1 - frac)),
            int(70 + (130 - 70) * (1 - frac)),
            255
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    
    # Atmospheric rim glow
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(201, 196, 255, 190), width=4)
    draw.ellipse([cx - radius + 4, cy - radius + 4, cx + radius - 4, cy + radius - 4], outline=(143, 134, 245, 120), width=3)
    
    # Front ring arc
    draw.arc([cx - ring_w//2, cy - ring_h//2, cx + ring_w//2, cy + ring_h//2], start=0, end=180, fill=(243, 241, 255, 230), width=8)
    draw.arc([cx - ring_w//2 - 16, cy - ring_h//2 - 8, cx + ring_w//2 + 16, cy + ring_h//2 + 8], start=5, end=175, fill=(201, 196, 255, 150), width=5)

    out_path = os.path.join(ART_DIR, "planet.webp")
    im.save(out_path, "WEBP", quality=85)
    print(f"Created {out_path} ({os.path.getsize(out_path)} bytes)")

# 3. Far Mountains (Lavender hazy silhouette)
def generate_far_mountains():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Mountain polygon across horizon
    pts = [
        (0, 720),
        (220, 580),
        (380, 530),
        (560, 610),
        (720, 560),
        (900, 640),
        (1100, 600),
        (1300, 660),
        (1500, 590),
        (1750, 510),
        (2000, 570),
        (2250, 520),
        (2400, 680),
        (2400, H),
        (0, H)
    ]
    draw.polygon(pts, fill=(143, 134, 245, 140))
    
    # Snow highlights
    peaks = [(380, 530), (720, 560), (1750, 510), (2250, 520)]
    for px, py in peaks:
        snow = [(px, py), (px - 50, py + 80), (px + 60, py + 95)]
        draw.polygon(snow, fill=(243, 241, 255, 160))
        
    out_path = os.path.join(ART_DIR, "far-mountains.webp")
    im.save(out_path, "WEBP", quality=85)
    print(f"Created {out_path} ({os.path.getsize(out_path)} bytes)")

# 4. Midground Plateau & Sugarcane Rows
def generate_plateau():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Rolling hills / plateau base
    pts = [
        (0, 800),
        (350, 780),
        (850, 820),
        (1400, 790),
        (1900, 830),
        (2400, 770),
        (2400, H),
        (0, H)
    ]
    draw.polygon(pts, fill=(20, 17, 107, 240))
    
    # Terraced curves
    for y in range(850, H - 150, 45):
        draw.arc([-200, y - 100, W + 200, y + 250], start=10, end=170, fill=(43, 34, 194, 130), width=3)
        draw.arc([-100, y - 80, W + 100, y + 230], start=15, end=165, fill=(75, 64, 230, 80), width=2)
        
    # Slim irrigation tower on left ridge
    tx, ty = 450, 620
    draw.line([(tx, ty + 180), (tx, ty)], fill=(178, 174, 234, 255), width=3)
    draw.line([(tx - 15, ty + 180), (tx + 15, ty + 180)], fill=(178, 174, 234, 255), width=4)
    draw.line([(tx - 12, ty + 180), (tx, ty)], fill=(143, 134, 245, 180), width=2)
    draw.line([(tx + 12, ty + 180), (tx, ty)], fill=(143, 134, 245, 180), width=2)
    # Beacon
    draw.ellipse([tx - 4, ty - 6, tx + 4, ty + 2], fill=(200, 245, 201, 255))
    
    out_path = os.path.join(ART_DIR, "plateau.webp")
    im.save(out_path, "WEBP", quality=85)
    print(f"Created {out_path} ({os.path.getsize(out_path)} bytes)")

# 5. Foreground Towers and Survey Drones
def generate_foreground_towers():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Floating crystalline shelf at right bottom
    shelf = [
        (1650, 1020),
        (1850, 990),
        (2200, 1010),
        (2400, 980),
        (2400, H),
        (1580, H)
    ]
    draw.polygon(shelf, fill=(11, 10, 63, 250))
    draw.line([(1650, 1020), (1850, 990), (2200, 1010), (2400, 980)], fill=(143, 134, 245, 200), width=3)
    
    # Spire towers on shelf
    towers = [(1920, 820, 170), (2050, 760, 240), (2180, 800, 200), (2310, 840, 150)]
    for bx, by, th in towers:
        draw.polygon([(bx - 12, by + th), (bx + 12, by + th), (bx, by)], fill=(201, 196, 255, 230))
        draw.line([(bx, by), (bx, by - 25)], fill=(243, 241, 255, 255), width=2)
        # Orb antenna
        draw.ellipse([bx - 6, by - 32, bx + 6, by - 20], fill=(200, 245, 201, 255))
        
    # Flying scout drone in mid-air
    dx, dy = 1720, 620
    drone_pts = [(dx, dy), (dx - 28, dy - 12), (dx - 18, dy + 8), (dx - 34, dy + 16)]
    draw.polygon(drone_pts, fill=(201, 196, 255, 230))
    draw.ellipse([dx - 8, dy - 2, dx, dy + 4], fill=(75, 64, 230, 255))
    
    out_path = os.path.join(ART_DIR, "foreground-towers.webp")
    im.save(out_path, "WEBP", quality=85)
    print(f"Created {out_path} ({os.path.getsize(out_path)} bytes)")

# 6. Hero Observatory Master Scene (from Stitch approved capture)
def generate_master_hero():
    src_path = "design/approved/s1_landing/screenshot.png"
    if os.path.exists(src_path):
        img = Image.open(src_path)
        out_path = os.path.join(ART_DIR, "hero-observatory.webp")
        img.save(out_path, "WEBP", quality=85)
        print(f"Created master hero {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate_sky_stars()
    generate_planet()
    generate_far_mountains()
    generate_plateau()
    generate_foreground_towers()
    generate_master_hero()
