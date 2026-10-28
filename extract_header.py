import fitz

def extract_header():
    pdf_path = "TravelSync Proposal Report.pdf"
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Define a rectangle for the header
    # 72 points = 1 inch. We'll take the top 140 points which should cover the logos and text.
    rect = fitz.Rect(0, 0, page.rect.width, 150)
    
    # Render the cropped region to a super high-res image
    pix = page.get_pixmap(clip=rect, dpi=600)
    pix.save("header.png")
    print("Extracted header.png successfully.")

if __name__ == "__main__":
    extract_header()
