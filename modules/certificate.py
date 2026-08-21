import io
from PIL import Image, ImageDraw, ImageFont
import os

def generate_certificate(student_name, quiz_title, score):
    """
    Loads your custom certificate template and stamps ONLY the student's name onto it.
    """
    template_path = "assets/certificate_template.png"
    
    if os.path.exists(template_path):
        try:
            image = Image.open(template_path).convert("RGB")
        except Exception:
            image = Image.new("RGB", (1200, 850), color="#f8fafc")
    else:
        image = Image.new("RGB", (1200, 850), color="#f8fafc")
    
    draw = ImageDraw.Draw(image)
    width, height = image.size

    try:
        # Load custom font or fallback with a large size for mobile clarity
        title_font = ImageFont.truetype("usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 1000)
    except:
        title_font = ImageFont.load_default()

    # Position for the student's name (center ribbon line)
    name_y_position = int(height * 0.45)
    
    # Draw ONLY the student name (with optional horizontal offset if you need to nudge it right later, e.g., (width / 2) + 40)
    draw.text((width / 2, name_y_position), student_name.upper(), fill="#0f172a", anchor="ms", font=title_font)

    # Save to memory buffer
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer