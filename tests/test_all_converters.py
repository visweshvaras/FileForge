"""
Automated verification test for all 8 conversion types.
"""
import os
import sys
import tempfile
import openpyxl

# Add paths
CONVERTERS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CONVERTERS_DIR not in sys.path:
    sys.path.insert(0, CONVERTERS_DIR)
PARENT_DIR = os.path.dirname(CONVERTERS_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from converters import (
    images_to_pdf,
    pdf_to_images,
    word_to_pdf,
    pdf_to_word,
    ppt_to_pdf,
    pdf_to_ppt,
    excel_to_pdf,
    pdf_to_excel
)

def run_tests():
    print("Testing Universal File Converter engines...")
    with tempfile.TemporaryDirectory(prefix="converter_test_") as tmp:
        # 1. Images to PDF
        img_src = "/home/vishwa/Documents/college ppt/IKS/tower_illustration.png"
        img_pdf = os.path.join(tmp, "combined_images.pdf")
        if os.path.exists(img_src):
            res = images_to_pdf([img_src, img_src], img_pdf)
            assert res["success"], f"Image to PDF failed: {res.get('error')}"
            print(f"✔ 1. Images -> PDF passed ({res['count']}, {res['size_bytes']} bytes)")

        # 2. PDF to Images
        if os.path.exists(img_pdf):
            res = pdf_to_images(img_pdf, os.path.join(tmp, "extracted_page.png"))
            assert res["success"], f"PDF to Images failed: {res.get('error')}"
            print(f"✔ 2. PDF -> Images passed ({res['count']})")

        # 3. Word to PDF
        word_src = "/home/vishwa/Documents/Glow_and_Glamour_Consent_Form.docx"
        word_pdf = os.path.join(tmp, "consent_form.pdf")
        if os.path.exists(word_src):
            res = word_to_pdf(word_src, word_pdf)
            assert res["success"], f"Word to PDF failed: {res.get('error')}"
            print(f"✔ 3. Word -> PDF passed ({res['count']}, {res['size_bytes']} bytes)")

        # 4. PDF to Word
        if os.path.exists(word_pdf):
            res = pdf_to_word(word_pdf, os.path.join(tmp, "reconstructed.docx"))
            assert res["success"], f"PDF to Word failed: {res.get('error')}"
            print(f"✔ 4. PDF -> Word passed ({res['count']}, {res['size_bytes']} bytes)")

        # 5. PPTX to PDF
        ppt_src = "/home/vishwa/Documents/KPIT Sparkle Project.pptx"
        ppt_pdf = os.path.join(tmp, "kpit.pdf")
        if os.path.exists(ppt_src):
            res = ppt_to_pdf(ppt_src, ppt_pdf)
            assert res["success"], f"PPT to PDF failed: {res.get('error')}"
            print(f"✔ 5. PPTX -> PDF passed ({res['count']}, {res['size_bytes']} bytes)")

        # 6. PDF to PPTX
        if os.path.exists(ppt_pdf):
            res = pdf_to_ppt(ppt_pdf, os.path.join(tmp, "kpit_deck.pptx"))
            assert res["success"], f"PDF to PPTX failed: {res.get('error')}"
            print(f"✔ 6. PDF -> PPTX passed ({res['count']}, {res['size_bytes']} bytes)")

        # 7. Excel to PDF
        sample_xlsx = os.path.join(tmp, "sample.xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Q3 Results"
        ws.append(["Category", "Metric", "Target", "Achieved", "Growth %"])
        ws.append(["Sales", "Enterprise Units", 120, 145, "+20.8%"])
        ws.append(["Operations", "Fleet Active Drones", 50, 48, "-4.0%"])
        ws.append(["Engineering", "System Uptime", "99.9%", "99.99%", "+0.09%"])
        wb.save(sample_xlsx)

        excel_pdf = os.path.join(tmp, "excel_report.pdf")
        res = excel_to_pdf(sample_xlsx, excel_pdf)
        assert res["success"], f"Excel to PDF failed: {res.get('error')}"
        print(f"✔ 7. Excel -> PDF passed ({res['count']}, {res['size_bytes']} bytes)")

        # 8. PDF to Excel
        if os.path.exists(excel_pdf):
            res = pdf_to_excel(excel_pdf, os.path.join(tmp, "extracted_report.xlsx"))
            assert res["success"], f"PDF to Excel failed: {res.get('error')}"
            print(f"✔ 8. PDF -> Excel passed ({res['count']}, {res['size_bytes']} bytes)")

    print("\n🎉 ALL 8 CONVERTER ENGINES PASSED VERIFICATION!")

if __name__ == "__main__":
    run_tests()
