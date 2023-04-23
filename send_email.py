import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
def email_sender(mail_host,mail_user,mail_pass,sender,receivers,context,content,zhunquelv):
    #邮件内容设置
    msg = MIMEMultipart()
    #邮件主题       
    msg['Subject'] = context
    #发送方信息
    msg['From'] = sender 
    #接受方信息     
    msg['To'] = ','.join(receivers)  
    #html_img = f'<p>{content}<br><img src="cid:image1"></br></p>'
    explain = '大周期指标（按年记）：Puell Multiple，BTC MVRV Z-Score，RHODL Ratio， 50MA aSOPR \
               中周期指标（按周记）：7MA NRPL，7MA aSOPR \
               短周期指标（按日记）：aSOPR，Futures Long Liquidations Dominance \
               Puell Multiple：大于4预示牛顶，小于0.5预示熊底 \
               BTC MVRV Z-Score: 大于7预示牛顶，小于0预示熊底 \
               RHODL Ratio: 大于10.8预示牛顶，小于5.86预示熊底 \
               50MA aSOPR :小于0.94预示熊底 \
               7MA NRPL: 小于0，预示短期底部，可以进行低吸 \
               7MA aSOPR：小于1，预示短期底部，可以进行低吸 \
               aSOPR：小于1，预示全网陷入亏损，可以尝试定投 \
               ETH P/BTC P: ETH价格/BTC价格，可以观察ETH的价格是不是被低估 \
               Futures Long Liquidations Dominance: 大于0.5说明合约中多头优势，小于0.5说明合约中空头优势 '
    message_1 = MIMEText(explain,'html','utf-8')
    msg.attach(message_1)

    text = '按照合约占比投资，准确率为：'+str(zhunquelv)
    message_2 = MIMEText(text,'html','utf-8')
    msg.attach(message_2)

    message = MIMEText(content,'html','utf-8')
    msg.attach(message)

    jpgpart = MIMEImage(open('/root/meaasge_pre/chain_data_picture.png', 'rb').read())
    jpgpart.add_header('Content-Disposition', 'attachment', filename='chain_data_picture.jpg')
    msg.attach(jpgpart)
    #msg.attach(MIMEText(html_img,'html','utf-8')) 
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