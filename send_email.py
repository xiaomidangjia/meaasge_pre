import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
def email_sender(mail_host,mail_user,mail_pass,sender,receivers,context,content):
    #邮件内容设置
    msg = MIMEMultipart()
    #邮件主题       
    msg['Subject'] = context
    #发送方信息
    msg['From'] = sender 
    #接受方信息     
    msg['To'] = receivers  
    
    message = MIMEText(content,'html','utf-8')
    msg.attach(message)

    jpgpart = MIMEApplication(open('/root/meaasage_pre/chain_data_picture.png', 'rb').read())
    jpgpart.add_header('Content-Disposition', 'attachment', filename='chain_data_picture.jpg')
    msg.attach(jpgpart)
    #登录并发送邮件
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        #连接到服务器
        #smtpObj.ehlo(mail_host)
        #登录到服务器
        smtpObj.login(mail_user,mail_pass) 
        #发送
        smtpObj.sendmail(
            sender,receivers,msg.as_string()) 
        #退出
        smtpObj.quit() 
        print('success')
    except smtplib.SMTPException as e:
        print('error',e) #打印错误