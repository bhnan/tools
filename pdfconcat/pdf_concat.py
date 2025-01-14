import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfMerger
import os

class PDFMergerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("PDF合并工具")
        self.window.geometry("600x400")
        
        self.pdf_files = []  # 存储选择的PDF文件路径
        
        # 创建界面元素
        self.create_widgets()
        
    def create_widgets(self):
        # 选择文件按钮
        select_btn = tk.Button(self.window, text="选择PDF文件", command=self.select_files)
        select_btn.pack(pady=10)
        
        # 显示选择的文件列表
        self.listbox = tk.Listbox(self.window, width=70, height=15)
        self.listbox.pack(pady=10)
        
        # 合并按钮
        merge_btn = tk.Button(self.window, text="合并PDF", command=self.merge_pdfs)
        merge_btn.pack(pady=10)
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf")]
        )
        
        # 将新选择的文件添加到现有列表中，而不是替换
        if len(self.pdf_files) + len(files) > 10:
            messagebox.showerror("错误", "最多只能选择10个PDF文件！")
            return
            
        self.pdf_files.extend(files)
        
        # 更新列表显示
        self.listbox.delete(0, tk.END)
        for file in self.pdf_files:
            self.listbox.insert(tk.END, os.path.basename(file))
            
    def merge_pdfs(self):
        if not self.pdf_files:
            messagebox.showwarning("警告", "请先选择PDF文件！")
            return
            
        try:
            # 使用第一个PDF文件名作为默认保存名
            default_filename = os.path.splitext(os.path.basename(self.pdf_files[0]))[0] + "_merged.pdf"
            
            # 选择保存位置
            save_path = filedialog.asksaveasfilename(
                initialfile=default_filename,
                defaultextension=".pdf",
                filetypes=[("PDF文件", "*.pdf")]
            )
            
            if save_path:
                merger = PdfMerger()
                
                # 添加所有PDF文件
                for pdf in self.pdf_files:
                    merger.append(pdf)
                
                # 保存合并后的文件
                merger.write(save_path)
                merger.close()
                
                messagebox.showinfo("成功", "PDF合并完成！")
                
        except Exception as e:
            messagebox.showerror("错误", f"合并过程中出现错误：{str(e)}")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PDFMergerGUI()
    app.run()
