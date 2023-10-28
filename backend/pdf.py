import fitz  # PyMuPDF
from PIL import Image
import tempfile
import os, shutil

def generate_pdf(images):
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print('temp_dir', temp_dir)
    try:
        pdf_document = fitz.open()  # 创建一个新的空白PDF文档
        
        # 设置A4纸的尺寸和分辨率
        a4_width_in_inches = 8.3
        a4_height_in_inches = 11.7
        dpi = 300  # dots per inch
        a4_width_in_pixels = int(a4_width_in_inches * dpi)
        a4_height_in_pixels = int(a4_height_in_inches * dpi)

        for i, img in enumerate(images):
            # 调整图像大小以适应A4纸
            img_resized = img.resize((a4_width_in_pixels, a4_height_in_pixels), Image.LANCZOS)
            
            # 保存每张图像到临时目录
            temp_img_path = os.path.join(temp_dir, f'image{i}.jpg')
            img_resized.save(temp_img_path, format='JPEG', quality=85)  # quality参数范围是0（最低质量，最小文件大小）到100（最高质量，最大文件大小）
            
            # 创建新页面
            pdf_page = pdf_document.new_page(width=a4_width_in_pixels, height=a4_height_in_pixels)
            
            # 定义插入图像的矩形区域
            rect = fitz.Rect(0, 0, a4_width_in_pixels, a4_height_in_pixels)
            
            # 插入图像到PDF页面
            pdf_page.insert_image(rect, filename=temp_img_path)
        
        # 创建临时PDF文件名
        temp_pdf_file_path = tempfile.mktemp(suffix='.pdf', dir='./temp')

        # 保存PDF文档到临时文件
        pdf_document.save(temp_pdf_file_path)

        # 关闭PDF文档
        pdf_document.close()
        return temp_pdf_file_path  # 返回 pdf 路径
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 清理临时目录及其内容
        shutil.rmtree(temp_dir)

# 调用示例
# 假设 images 是一个包含PIL Image对象的列表
# pdf_path = generate_pdf(images)
