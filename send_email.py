import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

def send_email_with_attachment(pdf_path=None):
    """
    通过QQ邮箱发送带附件的邮件
    """
    # QQ邮箱SMTP服务器配置
    smtp_server = "smtp.qq.com"
    smtp_port = 587
    
    # 从环境变量获取发件人邮箱和授权码
    sender_email = os.environ.get("QQ_EMAIL")
    password = os.environ.get("QQ_EMAIL_AUTH_CODE")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    
    if not all([sender_email, password, receiver_email]):
        print("错误: 请设置所有必要的环境变量")
        print("需要设置的环境变量:")
        print("  - QQ_EMAIL: 你的QQ邮箱")
        print("  - QQ_EMAIL_AUTH_CODE: QQ邮箱授权码")
        print("  - RECEIVER_EMAIL: 接收邮箱")
        return False
    
    # 邮件内容
    date_str = datetime.now().strftime("%Y年%m月%d日")
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    if pdf_path and os.path.exists(pdf_path):
        subject = f"The Economist 期刊 - {date_str}"
        body = f"""
        <html>
        <body>
            <h2>The Economist 期刊</h2>
            <p>附件是 {date_str} 的最新一期 The Economist 期刊。</p>
            <p>此邮件由GitHub Actions自动发送。</p>
            <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        # 添加PDF附件
        with open(pdf_path, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', 
                            filename=os.path.basename(pdf_path))
            msg.attach(attach)
        
        print(f"已添加附件: {pdf_path}")
        print(f"附件大小: {os.path.getsize(pdf_path) / 1024 / 1024:.2f} MB")
    else:
        subject = f"The Economist 期刊下载失败 - {date_str}"
        body = f"""
        <html>
        <body>
            <h2>The Economist 期刊下载失败</h2>
            <p>在 {date_str} 未能成功下载 The Economist 期刊。</p>
            <p>可能原因：</p>
            <ul>
                <li>网站页面结构可能已更改</li>
                <li>网络连接问题</li>
                <li>期刊未更新</li>
            </ul>
            <p>此邮件由GitHub Actions自动发送。</p>
            <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        print("未找到PDF文件，发送通知邮件")
    
    try:
        # 连接SMTP服务器并发送
        print(f"正在连接SMTP服务器: {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls()  # 启用TLS加密
        print("正在登录邮箱...")
        server.login(sender_email, password)
        print("正在发送邮件...")
        server.send_message(msg)
        server.quit()
        print("邮件发送成功！")
        return True
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 从命令行参数获取PDF路径
    pdf_path = None
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # 尝试查找最新的PDF文件
        import glob
        pdf_files = glob.glob("The_Economist_*.pdf")
        if pdf_files:
            # 按修改时间排序，取最新的
            pdf_files.sort(key=os.path.getmtime, reverse=True)
            pdf_path = pdf_files[0]
    
    success = send_email_with_attachment(pdf_path)
    sys.exit(0 if success else 1)