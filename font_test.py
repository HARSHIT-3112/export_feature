from fpdf import FPDF

pdf = FPDF()
pdf.add_font("DejaVuSans", "", "app/fonts/DejaVuSans.ttf", uni=True)
pdf.add_font("DejaVuSans", "B", "app/fonts/DejaVuSans-Bold.ttf", uni=True)
pdf.add_page()
pdf.set_font("DejaVuSans", "", 14)
pdf.cell(0, 10, "Unicode test — नमस्ते 😄", ln=True)
pdf.output("font_test.pdf")
print("✅ PDF created.")
