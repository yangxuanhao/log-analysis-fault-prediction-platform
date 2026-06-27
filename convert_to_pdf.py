# -*- coding: utf-8 -*-
"""使用Word将docx转换为PDF"""
import os, sys
import win32com.client

DOCX_PATH = os.path.abspath('操作手册.docx')
PDF_PATH = os.path.abspath('操作手册.pdf')

def convert_docx_to_pdf(docx_path, pdf_path):
    word = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        print(f'打开文档: {docx_path}')
        doc = word.Documents.Open(docx_path)
        print(f'转换为PDF: {pdf_path}')
        doc.SaveAs(pdf_path, FileFormat=17)  # wdFormatPDF
        doc.Close()
        print('转换完成！')
        return True
    except Exception as e:
        print(f'转换失败: {e}')
        return False
    finally:
        if word:
            try: word.Quit()
            except: pass

if __name__ == '__main__':
    if not os.path.exists(DOCX_PATH):
        print(f'❌ 找不到源文件: {DOCX_PATH}')
        sys.exit(1)
    print(f'源: {DOCX_PATH}')
    print(f'目标: {PDF_PATH}')
    if convert_docx_to_pdf(DOCX_PATH, PDF_PATH):
        size_mb = os.path.getsize(PDF_PATH) / (1024 * 1024)
        print(f'✅ PDF已生成 ({size_mb:.1f} MB)')
    else:
        print('❌ 失败')
        sys.exit(1)
