"""模型控制程序(MCP)工具模块 - 用于文档格式转换和文件管理"""
import os
import markdown
from weasyprint import HTML
from datetime import datetime
from typing import Dict, Any, Optional


class MCPTool:
    """
    模型控制程序工具类，提供文档转换和文件管理功能
    """
    
    def __init__(self, workspace_dir: Optional[str] = None):
        """
        初始化MCP工具
        
        Args:
            workspace_dir: 工作空间目录路径，如果为None则使用默认路径
        """
        # 设置工作空间目录
        self.workspace_dir = workspace_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'workspace'
        )
        
        # 确保工作空间目录存在
        self._ensure_workspace_exists()
    
    def _ensure_workspace_exists(self):
        """
        确保工作空间目录存在，如果不存在则创建
        """
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)
            print(f"创建工作空间目录: {self.workspace_dir}")
    
    def markdown_to_file(self, markdown_content: str, filename: Optional[str] = None) -> str:
        """
        将Markdown内容保存为Markdown文件
        
        Args:
            markdown_content: Markdown格式的内容
            filename: 文件名，如果为None则自动生成
        
        Returns:
            保存的文件路径
        """
        # 如果没有提供文件名，则生成一个包含时间戳的文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{timestamp}.md"
        
        # 确保文件名以.md结尾
        if not filename.endswith('.md'):
            filename += '.md'
        
        # 构建完整的文件路径
        file_path = os.path.join(self.workspace_dir, filename)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Markdown文件已保存: {file_path}")
        return file_path
    
    def markdown_to_pdf(self, markdown_content: str, filename: Optional[str] = None, 
                       md_file_path: Optional[str] = None) -> str:
        """
        将Markdown内容转换为PDF文件
        
        Args:
            markdown_content: Markdown格式的内容
            filename: 文件名，如果为None则自动生成
            md_file_path: 已存在的Markdown文件路径，如果提供则直接读取该文件
        
        Returns:
            生成的PDF文件路径
        """
        # 确保有Markdown文件路径，这对于正确解析相对路径的图片很重要
        if md_file_path and os.path.exists(md_file_path):
            # 如果提供了现有文件，使用它
            actual_md_path = md_file_path
            with open(md_file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        else:
            # 否则创建一个临时Markdown文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_md_filename = f"temp_pdf_conversion_{timestamp}.md"
            actual_md_path = os.path.join(self.workspace_dir, temp_md_filename)
            with open(actual_md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        # 如果没有提供文件名，则生成一个包含时间戳的文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{timestamp}.pdf"
        
        # 确保文件名以.pdf结尾
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # 构建完整的文件路径
        pdf_path = os.path.join(self.workspace_dir, filename)
        
        # 获取Markdown文件所在目录，作为图片的基础URL
        base_url = f"file://{os.path.dirname(os.path.abspath(actual_md_path))}/"
        
        # 将Markdown转换为HTML
        html_content = markdown.markdown(markdown_content, extensions=[
            'fenced_code',  # 支持代码块
            'tables',       # 支持表格
            'toc',          # 支持目录
            'attr_list',    # 支持属性列表
            'md_in_html'    # 支持在HTML中嵌入Markdown
        ])
        
        # 添加基本的CSS样式
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>消费分析报告</title>
            <style>
                body {{
                    font-family: 'SimSun', 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }}
                code {{
                    font-family: 'Courier New', monospace;
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    padding-left: 16px;
                    margin-left: 0;
                    color: #666;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 20px auto;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # 将HTML转换为PDF，使用base_url参数确保图片正确加载
        HTML(string=html_content, base_url=base_url).write_pdf(pdf_path)
        
        print(f"PDF文件已生成: {pdf_path}")
        return pdf_path
    
    def convert_and_save(self, markdown_content: str, filename_prefix: Optional[str] = None) -> Dict[str, str]:
        """
        一步完成Markdown到文件的保存和PDF转换
        
        Args:
            markdown_content: Markdown格式的内容
            filename_prefix: 文件名前缀，如果为None则使用默认值
        
        Returns:
            包含md_path和pdf_path的字典
        """
        # 生成文件名前缀
        if not filename_prefix:
            filename_prefix = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存Markdown文件
        md_path = self.markdown_to_file(markdown_content, f"{filename_prefix}.md")
        
        # 转换为PDF文件，传入md_file_path参数以便正确处理图片路径
        pdf_path = self.markdown_to_pdf(None, f"{filename_prefix}.pdf", md_file_path=md_path)
        
        return {
            "md_path": md_path,
            "pdf_path": pdf_path,
            "workspace_dir": self.workspace_dir
        }


# 创建全局MCP工具实例
mcp_tool = MCPTool()


# 导出主要函数供其他模块使用
def save_markdown_and_convert_to_pdf(markdown_content: str, filename_prefix: Optional[str] = None) -> Dict[str, str]:
    """
    保存Markdown内容并转换为PDF的便捷函数
    
    Args:
        markdown_content: Markdown格式的内容
        filename_prefix: 文件名前缀
    
    Returns:
        包含md_path和pdf_path的字典
    """
    return mcp_tool.convert_and_save(markdown_content, filename_prefix)