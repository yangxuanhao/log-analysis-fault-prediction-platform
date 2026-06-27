# -*- coding: utf-8 -*-
"""完整流程：插入截图→生成PDF→打包"""
import os, sys, glob, shutil

PROJECT_DIR = r"D:\gzwj\信息系统运行日志智能分析与故障预测及根因定位平台"
SOURCE_DIR = os.path.join(PROJECT_DIR, "信息系统运行日志智能分析与故障预测及根因定位平台")
SCREENSHOT_DIR = os.path.join(PROJECT_DIR, "manual_screenshots")
DESKTOP_DIR = r"C:\Users\lenovo\Desktop"
DOCX_PATH = os.path.join(PROJECT_DIR, "操作手册.docx")
PDF_PATH = os.path.join(PROJECT_DIR, "操作手册.pdf")
TEMP_DOCX = os.path.join(PROJECT_DIR, "操作手册_补充版.docx")

os.chdir(PROJECT_DIR)

def run_cmd(cmd, desc):
    print(f"\n{'='*50}")
    print(f"Step: {desc}")
    print(f"{'='*50}")
    ret = os.system(cmd)
    if ret != 0:
        print(f"❌ {desc} 失败!")
        return False
    return True

# Step 1: 插入截图到docx
if not run_cmd('python insert_screenshots.py', '插入截图到文档'): sys.exit(1)

# 覆盖原文档
if os.path.exists(TEMP_DOCX):
    shutil.copy2(TEMP_DOCX, DOCX_PATH)
    os.remove(TEMP_DOCX)
    print(f"已覆盖: {DOCX_PATH}")

# Step 2: 生成PDF
if not run_cmd('python convert_to_pdf.py', '生成PDF'): sys.exit(1)

# 覆盖原PDF
temp_pdf = os.path.join(PROJECT_DIR, "操作手册_补充版.pdf")
if os.path.exists(temp_pdf):
    if os.path.exists(PDF_PATH): os.remove(PDF_PATH)
    shutil.move(temp_pdf, PDF_PATH)
    print(f"已覆盖: {PDF_PATH}")

# Step 3: 复制截图到桌面
print(f"\n{'='*50}\nStep: 复制截图到桌面\n{'='*50}")
desktop_shots = os.path.join(DESKTOP_DIR, "manual_screenshots")
if os.path.exists(desktop_shots): shutil.rmtree(desktop_shots)
shutil.copytree(SCREENSHOT_DIR, desktop_shots)
print(f"✅ 截图已复制到: {desktop_shots}")

# Step 4: 打包整个项目到桌面
print(f"\n{'='*50}\nStep: 打包项目到桌面\n{'='*50}")

# 创建临时打包目录
temp_zip_dir = os.path.join(DESKTOP_DIR, "_temp_zip_content")
if os.path.exists(temp_zip_dir): shutil.rmtree(temp_zip_dir)
os.makedirs(temp_zip_dir)

# 复制需要打包的内容
items_to_copy = {
    DOCX_PATH: "操作手册.docx",
    PDF_PATH: "操作手册.pdf",
    SCREENSHOT_DIR: "manual_screenshots",
    SOURCE_DIR: "信息系统运行日志智能分析与故障预测及根因定位平台",
    os.path.join(PROJECT_DIR, "申请表信息.txt"): "申请表信息.txt",
    os.path.join(PROJECT_DIR, "main.py"): "main.py",
    os.path.join(PROJECT_DIR, "requirements.txt"): "requirements.txt",
}

for src, dst_name in items_to_copy.items():
    dst = os.path.join(temp_zip_dir, dst_name)
    if os.path.exists(src):
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '.venv', '.idea'))
        else:
            shutil.copy2(src, dst)
        print(f"  + {dst_name}")
    else:
        print(f"  ⚠ 跳过: {src}")

# 创建zip
ZIP_NAME = "信息系统运行日志智能分析与故障预测及根因定位平台_完整项目.zip"
ZIP_PATH = os.path.join(DESKTOP_DIR, ZIP_NAME)
if os.path.exists(ZIP_PATH): os.remove(ZIP_PATH)

result = shutil.make_archive(ZIP_PATH.replace('.zip', ''), 'zip', temp_zip_dir)

# 清理临时目录
shutil.rmtree(temp_zip_dir)

if os.path.exists(ZIP_PATH):
    size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"\n✅ 打包完成! 大小: {size_mb:.1f} MB")
    print(f"   位置: {ZIP_PATH}")
else:
    print("❌ 打包失败")

print(f"\n✅ 全部流程完成!")
print(f"1. 操作手册.docx - 已更新（含操作截图）")
print(f"2. 操作手册.pdf - 已更新")
print(f"3. 截图已复制到桌面: {desktop_shots}")
print(f"4. 项目压缩包: {ZIP_PATH}")
