#!/usr/bin/env python
import os
import fitz
import extract   
import pikepdf
from pikepdf import ObjectStreamMode

def remove_headers_footers(input_pdf, output_pdf, header_height=50, footer_height=50):

    doc = fitz.open(input_pdf)
    for page in doc:
        rect = page.rect
        new_rect = fitz.Rect(rect.x0, rect.y0 + header_height, rect.x1, rect.y1 - footer_height)
        page.set_cropbox(new_rect)
    doc.save(output_pdf)
    doc.close()
    print(f"{output_pdf}")

def is_title_by_size(span, baseline_size=12, delta=2):

    size = span.get("size", 0)
    return size >= baseline_size + delta

def process_keyword_pages_by_title(clean_pdf, mapping, baseline_size=12, delta=2):

    doc = fitz.open(clean_pdf)
    for keyword, (orig_list, new_list) in mapping.items():
        folder_name = keyword.replace(" ", "_")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        print(f"{keyword}: {new_list}")
        sorted_pages = sorted(new_list)
        segments = []          
        current_segment = None 

        for page_num in sorted_pages:
            page = doc[page_num - 1]
            text_dict = page.get_text("dict")

            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue

                for line in block["lines"]:
                    for span in line["spans"]:

                        if is_title_by_size(span, baseline_size, delta):

                            if current_segment is not None and current_segment.strip():
                                segments.append(current_segment.strip())

                            current_segment = span["text"].strip() + "\n"
                        else:

                            if current_segment is not None:
                                current_segment += span["text"] + " "

                    if current_segment is not None:
                        current_segment += "\n"

        if current_segment is not None and current_segment.strip():
            segments.append(current_segment.strip())
  

        file_counter = 1
        for seg in segments:
            txt_filename = os.path.join(folder_name, f"{keyword.replace(' ', '_')}{file_counter}.txt")
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(seg)
            print(f"  Write: {txt_filename}")
            file_counter += 1
    doc.close()

def main():
    pdf_path = "catapult_useref.pdf"   
    output_pdf_path = "page.pdf"         
    clean_pdf = "clean.pdf"             

    keyword_ranges = {
        "pointer": (31, 1595),
        "dynamic memory": (31, 525),
        "recursion": (31, 546),
        "ac_int": (36, 39),
        "boolean": (370, 370),
        "case statement": (372, 373),
        "Non Synthesizable Constructs": (31, 1595),
        "bound": (365, 366),
    }

    ret = extract.extract_pages_by_keywords(pdf_path, keyword_ranges, output_pdf_path)
    if ret is None:
        print("extract_pages_by_keywords()")
        return
    mapping, new_order = ret
    
    print("\nMapping:")
    for keyword, (orig, new) in mapping.items():
        start, end = keyword_ranges.get(keyword, (0, 0))
        print(f"{keyword}（Range {start}-{end}）: orig: {orig}, new: {new}")
    
    remove_headers_footers(output_pdf_path, clean_pdf, header_height=62, footer_height=55)
    
    process_keyword_pages_by_title(clean_pdf, mapping)
    
    print("\nFinish！")

if __name__ == "__main__":
    main()
