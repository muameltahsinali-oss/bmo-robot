import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

def create_gradient(width, height, start_color, end_color):
    """Create a radial gradient image"""
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            # Distance from center
            dx = x - width/2
            dy = y - height/2
            dist = (dx*dx + dy*dy)**0.5
            # Max dist is corner
            max_dist = (width/2 * 1.414)
            ratio = min(dist / max_dist, 1.0)
            mask_data.append(int(ratio * 255))
    mask.putdata(mask_data)
    return Image.composite(top, base, mask)

def draw_face(size, expression):
    width, height = size
    
    # 1. Background (Teal Gradient)
    # Teal: #00d2be (BMO main), Darker: #009e8f
    bg = create_gradient(width, height, (100, 230, 210, 255), (0, 180, 160, 255))
    
    # Create a separate layer for features to manage transparency/shadows
    features = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(features)
    
    # Dimensions
    eye_radius = width * 0.08
    eye_y = height * 0.4
    left_eye_x = width * 0.35
    right_eye_x = width * 0.65
    
    shadow_offset = width * 0.02
    
    # Colors
    eye_color = (250, 255, 245, 255) # Off-white
    shadow_color = (0, 80, 70, 100)  # Dark teal shadow
    
    def draw_eye_shadow(x, y, r, type='circle'):
        # Draw shadow on a temp layer and blur it
        shadow = Image.new('RGBA', (width, height), (0,0,0,0))
        s_draw = ImageDraw.Draw(shadow)
        if type == 'circle':
            s_draw.ellipse([x-r, y-r + shadow_offset, x+r, y+r + shadow_offset], fill=shadow_color)
        elif type == 'line':
             s_draw.line([x-r, y + shadow_offset, x+r, y + shadow_offset], fill=shadow_color, width=int(r/2))
        elif type == 'arc':
             s_draw.arc([x-r, y-r + shadow_offset, x+r, y+r + shadow_offset], 180, 360, fill=shadow_color, width=int(r/2))
             
        # Blur
        return shadow.filter(ImageFilter.GaussianBlur(radius=width*0.01))

    # --- Draw Eyes ---
    if expression == 'idle':
        # Shadows
        s1 = draw_eye_shadow(left_eye_x, eye_y, eye_radius)
        s2 = draw_eye_shadow(right_eye_x, eye_y, eye_radius)
        bg = Image.alpha_composite(bg, s1)
        bg = Image.alpha_composite(bg, s2)
        
        # Eyes
        draw.ellipse([left_eye_x-eye_radius, eye_y-eye_radius, left_eye_x+eye_radius, eye_y+eye_radius], fill=eye_color)
        draw.ellipse([right_eye_x-eye_radius, eye_y-eye_radius, right_eye_x+eye_radius, eye_y+eye_radius], fill=eye_color)
        
        # Highlights
        h_r = eye_radius * 0.3
        h_offset = eye_radius * 0.4
        draw.ellipse([left_eye_x-h_offset-h_r, eye_y-h_offset-h_r, left_eye_x-h_offset+h_r, eye_y-h_offset+h_r], fill=(255,255,255,255))
        draw.ellipse([right_eye_x-h_offset-h_r, eye_y-h_offset-h_r, right_eye_x-h_offset+h_r, eye_y-h_offset+h_r], fill=(255,255,255,255))

    elif expression == 'blink':
        # Shadows
        # s1 = draw_eye_shadow(left_eye_x, eye_y, eye_radius, 'line') # Shadows look weird on blink lines sometimes
        # Let's skip shadow for blink lines for cleaner look, or do very subtle
        
        # Eyes (Lines)
        line_w = width * 0.12
        thick = int(width * 0.03)
        draw.line([left_eye_x - line_w/2, eye_y, left_eye_x + line_w/2, eye_y], fill=eye_color, width=thick)
        draw.line([right_eye_x - line_w/2, eye_y, right_eye_x + line_w/2, eye_y], fill=eye_color, width=thick)

    elif expression == 'happy':
        # Inverted Arcs (Squint)
        arc_r = eye_radius * 1.2
        thick = int(width * 0.03)
        # Bounding box for arc
        bbox_l = [left_eye_x - arc_r, eye_y - arc_r, left_eye_x + arc_r, eye_y + arc_r]
        bbox_r = [right_eye_x - arc_r, eye_y - arc_r, right_eye_x + arc_r, eye_y + arc_r]
        
        draw.arc(bbox_l, 180, 360, fill=eye_color, width=thick)
        draw.arc(bbox_r, 180, 360, fill=eye_color, width=thick)

    # --- Draw Mouth ---
    mouth_y = height * 0.65
    mouth_w = width * 0.15
    mouth_h = height * 0.1
    thick = int(width * 0.025)
    
    if expression == 'happy':
        mouth_w = width * 0.25
        mouth_h = height * 0.15
        # Open mouth D shape? Or just big curve? BMO has a line usually.
        # "Big open smile" in prompt. Let's do a D shape.
        draw.chord([width/2 - mouth_w, mouth_y - mouth_h, width/2 + mouth_w, mouth_y + mouth_h], 0, 180, fill=eye_color)
    elif expression == 'speaking':
        # "O" mouth
        r = width * 0.05
        draw.ellipse([width/2 - r, mouth_y - r, width/2 + r, mouth_y + r], fill=eye_color)
    else:
        # Simple Smile
        draw.arc([width/2 - mouth_w, mouth_y - mouth_h, width/2 + mouth_w, mouth_y + mouth_h], 0, 180, fill=eye_color, width=thick)

    # Composite Features onto BG
    final = Image.alpha_composite(bg, features)
    return final

def generate_assets():
    sizes = [(320, 320), (240, 240)]
    states = ['idle', 'blink', 'happy']
    
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    for size in sizes:
        for state in states:
            img = draw_face(size, state)
            
            # Filename
            # User asked for 'assets/bmo_face_idle.png' etc without size in name?
            # They requested specific files. I should probably save the MAIN size (320) as the default name
            # And maybe the 240 size with a suffix, or just overwrite since they asked for "Export both sizes".
            # "Export both sizes" usually implies different filenames or folders.
            # I will save 320 as default, and 240 as `_small`.
            
            # Actually user listed exact filenames:
            # assets/bmo_face_idle.png
            # ...
            # I will use 320x320 for these main files as it's higher res (downscaleable).
            
            if size == (320, 320):
                name = f"bmo_face_{state}"
                img.save(os.path.join(base_dir, f"{name}.png"))
                img.save(os.path.join(base_dir, f"{name}.webp"))
                print(f"Saved {name} (320x320)")
            
            # If they really need 240x240, I'll save as `_240`.
            if size == (240, 240):
                name = f"bmo_face_{state}_240"
                img.save(os.path.join(base_dir, f"{name}.png"))
                img.save(os.path.join(base_dir, f"{name}.webp"))
                print(f"Saved {name} (240x240)")

if __name__ == "__main__":
    generate_assets()
