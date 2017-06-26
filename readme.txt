本程序基于Python 编写,用于新版正方教务系统的教务评价
程序分为如下模块:
    manager.py          用于整体管理程序的运行

    recv_info.py        接收用于订单和管理员的工单
                        此模块基于www.mikecrm.com 的表单服务,从通知邮件中解析获取用户信息
                        通知邮件分为两个文件夹"yjpj_payment"(订单) 和 "work_order" (工单)

    process_order.py    对用户的订单进行处理,包括检查密码是否正确和进行刷评价
                        调用send_mail进行通知的推送

    JwUser.py           教务系统的处理,检测密码,刷评价,以及其他可拓展的功能 是最核心的模块,

    send_mail.py        发送邮件的模块

    const.py            常用的设置项,需要根据需要更改

    log.py              设置日志

    附加的python包在requirement.txt文件

    使用方法:
        JwUser 可以直接用于刷评价,对于不同的网站需要在const.py 内更改对应的网址
        其他的文件根据需要自行更改移植
