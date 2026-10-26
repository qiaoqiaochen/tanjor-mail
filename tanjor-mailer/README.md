# Tanjor 邮件发送程序

尚未部署，默认模拟，不发送邮件。仅支持网易提供的SSL SMTP端口465；服务器地址应以邮箱官方设置为准，不猜测。

## 配置步骤

1. 建立GitHub私有仓库，上传本目录全部内容，包括.github/workflows/send.yml。不要上传任何密码或JSON密钥文件。
2. 在Google Cloud建立项目，启用Google Sheets API，创建服务账号和JSON密钥。将目标表格以编辑权限共享给该服务账号的client_email。无需将表格公开。密钥仅填入下一步的GitHub Secret。
3. GitHub仓库 Settings → Secrets and variables → Actions，建立三个Secrets：GOOGLE_SERVICE_ACCOUNT_JSON（完整JSON）、SMTP_HOST（网易官方SSL SMTP地址）、SMTP_PASSWORD（客户端授权码）。
4. 在“邮件草稿”F列原生表下拉增加“批准发送”“发送中”“需核查”；G1添加“发送时间”，H1添加“发送结果”。将TanjorDrafts原生表扩展至H列，为新增G:H列使用TEXT类型，保留原有数据。当前程序遇到不匹配表头会停止，不会自行改表。
5. 先只选一封发给自己邮箱的测试邮件，状态设“批准发送”。Actions → Approved email sender → Run workflow。默认模拟，日志显示ready，不改状态、不发送。
6. 模拟通过后，建立仓库Variable DRY_RUN，值为false，再手动运行一次，确认收信和表格回写。真实客户邮件在测试通过前不要批准。
7. 程序UTC每天23:47运行（阿德莱德夏令时次日10:17、标准时次日09:17），可能延迟。每日最多5封；改回DRY_RUN=true即可暂停真实发送，也可在Actions禁用工作流。

## 使用

每封发出的正文就是E列全部文字，请先确认正文含签名。仅F列为“批准发送”且G:H为空的行会发送。已有“待发送”邮件不会发送。程序不读取收件箱，不自动跟进，不调用AI，不添加追踪图片。

发送中断或结果不确定时保持“发送中”或“需核查”，不得直接清空结果重发：先核对邮箱和收件情况。SMTP已接受不代表最终投递成功；退信仍需查看。SMTP发送可能不会出现在网页“已发送”中，取决于邮箱服务设置。

首次运行前确认GitHub免费额度并限制付费使用；不需要购买服务器。Google Cloud只启用本程序所需Sheets API，不启用付费产品。未来平台政策变化应重新核对。

本程序已进行Python语法检查；未连接真实SMTP或Google服务账号，尚未进行端到端发送测试。
