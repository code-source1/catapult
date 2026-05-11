import fitz
import pikepdf
from pikepdf import ObjectStreamMode
import os

def extract_pages_by_keywords(pdf_path, keyword_ranges, output_pdf_path):

    doc = fitz.open(pdf_path)

    keyword_pages = {}
    for keyword, (start_page, end_page) in keyword_ranges.items():
        pages_found = []

        start = max(0, start_page - 1)
        end = min(end_page, len(doc))
        for i in range(start, end):
            text = doc[i].get_text("text")
            if keyword.lower() in text.lower():
                pages_found.append(i + 1)

        keyword_pages[keyword] = sorted(pages_found)

    new_order = []   
    mapping = {}     
    new_page_counter = 1
    for keyword in keyword_ranges.keys():
        orig_pages = keyword_pages.get(keyword, [])
        new_pages = list(range(new_page_counter, new_page_counter + len(orig_pages)))
        new_page_counter += len(orig_pages)
        mapping[keyword] = (orig_pages, new_pages)
        new_order.extend(orig_pages)

    print("Mapping:")
    for keyword, (start, end) in keyword_ranges.items():
        orig, new = mapping.get(keyword, ([], []))
        print(f"{keyword}（Range {start}-{end}）: orig: {orig}, new: {new}")
    
    selected_pages = [p - 1 for p in new_order]
    doc.select(selected_pages)
    
    temp_pdf_path = "temp_page.pdf"
    doc.save(temp_pdf_path, garbage=4, deflate=True, clean=True)
    doc.close()
    
    with pikepdf.open(temp_pdf_path) as pdf:
        pdf.save(
            output_pdf_path,
            compress_streams=True,
            linearize=True,
            object_stream_mode=ObjectStreamMode.generate
        )
        
    os.remove(temp_pdf_path)
    print(f"\n新的 PDF 文件已保存至: {output_pdf_path}")
    return mapping, new_order

