from PIL import Image, ImageDraw, ImageFont

def draw_centered_text(draw, text, box, font, fill="black"):
    x1, y1, x2, y2 = box
    
    # Simple bounding box approximation
    try:
        bbox = draw.multiline_textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        lines = text.split('\n')
        text_width = max(len(line) for line in lines) * 10
        text_height = len(lines) * 20
        
    # Calculate position
    x = x1 + (x2 - x1 - text_width) / 2
    y = y1 + (y2 - y1 - text_height) / 2
    
    draw.multiline_text((x, y), text, fill=fill, font=font, align="center")

def create_architecture_diagram():
    # Setup image and drawing context
    width = 1200
    height = 900
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use Arial font if available
        font = ImageFont.truetype("arial.ttf", 20)
        title_font = ImageFont.truetype("arialbd.ttf", 36)
        small_font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
        title_font = font
        small_font = font
    
    # Title
    draw.text((350, 40), "System Architecture", fill="black", font=title_font)
    
    def draw_box(x, y, w, h, text, color="#E0F7FA"):
        draw.rectangle([x, y, x+w, y+h], fill=color, outline="black", width=2)
        draw_centered_text(draw, text, (x, y, x+w, y+h), font)

    def draw_arrow(x1, y1, x2, y2, label=""):
        draw.line([(x1, y1), (x2, y2)], fill="black", width=3)
        # draw simple arrowhead
        if y2 > y1:
            draw.polygon([(x2, y2), (x2-10, y2-15), (x2+10, y2-15)], fill="black")
        elif y1 > y2:
            draw.polygon([(x2, y2), (x2-10, y2+15), (x2+10, y2+15)], fill="black")
        
        if label:
            # draw background for text to make it readable
            tw = draw.textlength(label, font=small_font) if hasattr(draw, 'textlength') else len(label) * 8
            tx, ty = (x1+x2)/2 - tw/2, (y1+y2)/2 - 10
            draw.rectangle([tx-5, ty-2, tx+tw+5, ty+18], fill="white")
            draw.text((tx, ty), label, fill="gray", font=small_font)

    # 1. User
    draw_box(450, 120, 300, 60, "User / Web Browser", "#FFF9C4")
    
    # Arrow down
    draw_arrow(600, 180, 600, 260, "(HTTP Request)")
    
    # 2. Frontend
    draw_box(450, 260, 300, 80, "Streamlit Frontend\n(UI & Visualization)", "#E1BEE7")
    
    # Arrow down
    draw_arrow(600, 340, 600, 420, "(REST API / JSON)")
    
    # 3. Backend
    draw_box(450, 420, 300, 80, "Flask Backend API\n(Microservices Gateway)", "#C8E6C9")
    
    # Branching arrows down to 4 services
    draw_arrow(600, 500, 250, 580)
    draw_arrow(600, 500, 480, 580)
    draw_arrow(600, 500, 720, 580)
    draw_arrow(600, 500, 950, 580)
    
    # 4. Services
    draw_box(150, 580, 200, 60, "Stock Service\n(yfinance)", "#BBDEFB")
    draw_box(380, 580, 200, 60, "Indicator Service\n(Pandas TA)", "#BBDEFB")
    draw_box(620, 580, 200, 60, "Prediction Service\n(TensorFlow / ML)", "#BBDEFB")
    draw_box(850, 580, 200, 60, "Recommendation\n(Rules & Sentiment)", "#BBDEFB")
    
    # Arrows from services to data sources
    draw_arrow(250, 640, 250, 720, "API Calls")
    draw_arrow(720, 640, 720, 720, "I/O")
    draw_arrow(950, 640, 950, 720, "FinBERT")
    
    # 5. External / Disk
    draw_box(150, 720, 200, 60, "Yahoo Finance API", "#FFE0B2")
    draw_box(620, 720, 200, 60, "Local File System\n(.h5 Models / Scalers)", "#FFE0B2")
    draw_box(850, 720, 200, 60, "Transformer Models", "#FFE0B2")

    img.save("architecture.png")
    print("Saved architecture.png")

if __name__ == "__main__":
    create_architecture_diagram()
