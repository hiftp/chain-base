# -*- coding: utf-8 -*-
import datetime
import ftplib
import io
import logging
import random
import string
from decimal import Decimal
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
import socket
import os
from odoo.exceptions import UserError
from odoo.http import request
import sys
from ftplib import FTP

reload(sys)
sys.setdefaultencoding('utf-8')


class ABCFunctions(classmethod):

    @classmethod
    def send_tcp(cls, ip, port, xml_str):
        """
        使用tcp发送请求报文
        :param ip:IP地址
        :param port: 端口
        :param xml_str: xml报文
        :return result_xml :结果xml
        """
        xml_str = xml_str.decode('gbk')
        xml_str = cls.pack_xml_top(0, xml_str)
        logging.info(xml_str)
        address = (ip, int(port))
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(address)
        except socket.error:
            raise UserError(u"尝试连接到农业银行前置机发生错误！无法连接！")
        client.send(xml_str.encode(encoding='gbk'))
        data = client.recv(9999999)  # 接受响应信息
        data = data.decode('gbk')
        client.close()
        return data

    @classmethod
    def pack_xml_top(cls, sign, xml_str):
        """
        请求数据：sign加密标识（1加密,0不加密） + 请求xml数据的长度（默认7位，不够补空格） + 请求的xml
        :param sign: sign加密标识（1加密,0不加密）
        :param xml_str: 需要生成的xml
        :return: 请求的xml
        """
        xml_len = str(sign) + str(len(xml_str))
        i = 0
        while i < 7 - (len(xml_len)):
            xml_len = xml_len + ' '
        str_xml = '{}{}'.format(xml_len, xml_str)
        return str_xml

    @classmethod
    def get_strftime(cls):
        """获取当前时间的格式化字符串
        :return YYYYmmDD
        """
        now_time = datetime.datetime.now()
        return now_time.strftime('%Y%m%d')

    @classmethod
    def search_abc_bal(cls, accounts, currency_id):
        """查询农业银行账户余额xml
        :param accounts: 付款账户
        :param currency_id: 币种
        :return string : 返回查询xml
        """
        # 获取随机数用于流水号
        random = cls.get_random_str(25)
        # 企业操作员编号
        abc_operator_number = request.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = request.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = request.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        str_xml = {
            'CCTransCode': 'CQRA06',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': accounts[0].costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no,  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign,
            'Cmp': {
                'DbAccNo': accounts[0].payment_number,
                'DbProv': accounts[0].abc_pc.code if accounts[0].abc_pc else '22',
                'DbCur': currency_id.number
            }
        }
        str_xml = cls.dict_to_xml('ap', str_xml)
        return tostring(str_xml)

    @classmethod
    def dict_to_xml(cls, tag, dic):
        """将传递的dict转换为xml（不包含声明信息）
        :param tag: 转换节点名称
        :param dic: 需要转换的dict字典
        :return :Element Object 需要使用tostring方法获取字符串
        """
        elem = Element(tag)
        for key, val in dic.items():
            if isinstance(val, dict):
                elem.append(cls.dict_to_xml(key, val))
            else:
                child = Element(key)
                child.text = str(val)
                elem.append(child)
        return elem

    @classmethod
    def get_random_str(cls, num):
        """生成一个长度为 num 的随机字符串
        :param num 生成的长度
        :return string
        """
        return ''.join(random.sample(string.ascii_letters + string.digits, num))

    @classmethod
    def search_abc_tran_detail(cls, accounts, start_date, end_date, currency):
        """封装查询银行账户交易明细xml（CQRA10）
        :param accounts : 交易账户
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param currency: 币种
        :return string : xml字符串
        """
        # 获取随机数用于流水号
        random = cls.get_random_str(25)
        # 企业操作员编号
        abc_operator_number = request.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = request.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = request.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        StartDate = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        EndDate = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        str_xml = {
            'CCTransCode': 'CQRA10',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': accounts[0].costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number if abc_operator_number else '',  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Cmp': {
                'DbAccNo': accounts[0].payment_number,
                'DbProv': accounts.abc_pc.code,
                'DbCur': currency.number
            },
            'Corp': {
                'StartDate': StartDate.strftime('%Y%m%d'),  # 起始日期
                'EndDate': EndDate.strftime('%Y%m%d'),  # 终止日期
            },
            'Channel': {
                'LastJrnNo': '0'
            }
        }
        str_xml = cls.dict_to_xml('ap', str_xml)
        return tostring(str_xml)

    @classmethod
    def get_ftp_file(cls, filename):
        """根据文件名去ftp服务器下载文件
        :param filename 文件名
        """
        ftp_host = request.env['ir.values'].get_default('interface.bank.settings', 'ftp_host')
        ftp_port = request.env['ir.values'].get_default('interface.bank.settings', 'ftp_port')
        ftp_user = request.env['ir.values'].get_default('interface.bank.settings', 'ftp_user')
        ftp_pwd = request.env['ir.values'].get_default('interface.bank.settings', 'ftp_pwd')
        dir_ftp = request.env['ir.values'].get_default('interface.bank.settings', 'dir_ftp')
        cls.get_ftp_server_file(dir_ftp, filename,
                                ftp_host, ftp_port, ftp_user, ftp_pwd)
        return True

    @classmethod
    def up_ftp_file(cls, filename):
        """上传文件到ftp
        :param filename 文件名
        """
        ftp_host = request.env['ir.values'].get_default('interface.bank.settings', 'ftp_host')
        ftp_port = request.env['ir.values'].get_default('interface.bank.settings', 'ftp_port')
        ftp_user = request.env['ir.values'].get_default('interface.bank.settings', 'ftp_user')
        ftp_pwd = request.env['ir.values'].get_default('interface.bank.settings', 'ftp_pwd')
        dir_up_ftp = request.env['ir.values'].get_default('interface.bank.settings', 'dir_up_ftp')
        cls.up_ftp_server_file(dir_up_ftp, "AbcData/" + filename,
                               ftp_host, ftp_port, ftp_user, ftp_pwd)
        return True

    @classmethod
    def get_ftp_server_file(cls, dir_ftp, filename, host, port, username, password):
        """
        登陆 ftp 服务器下载文件（保存到项目根目录）
        :param dir_ftp: 目标文件在 ftp 服务器上路径；
        :param filename: 目标文件名；
        :param host: ftp 服务器地址（ip/域名）；
        :param port: ftp 服务器端口号，一般是 21；
        :param username: 登陆 ftp 服务器时的用户名
        :param password: 登陆 ftp 服务器时的密码
        :return boolean
        """
        if os.path.exists(filename):
            logging.info(u'FTP:文件 ' + filename + u' 已经存在！该文件将被重复写入')
        # 开始连接
        try:
            f = ftplib.FTP()
            f.connect(host=host, port=port)
        except (socket.error, socket.gaierror), e:
            msg = u"FTP: 不能连接到ftp服务器({})，请检查ftp服务器是否正常工作!".format(host)
            logging.info(msg)
            raise UserError(msg)
        # 登录
        try:
            f.login(user=username, passwd=password)
        except ftplib.error_perm, e:
            msg = u"Ftp: 不能登录到FTP服务器，请检查账户名和密码及端口是否正确！"
            f.quit()
            raise UserError(msg)
        msg = u"用户{}已登录ftp服务器{}".format(username, host)
        logging.info(msg)
        try:
            f.cwd(dir_ftp)
        except ftplib.error_perm, e:
            msg = u"FTP:路径{}在ftp服务器{}中无法打开！".format(dir_ftp, host)
            logging.info(msg)
            f.quit()
            raise UserError(msg)
        # 获取文件
        f.set_pasv(0)
        try:
            logging.info(u'>>>>>>>>>>>>下载文件 {} ... ...'.format(filename))
            buf_size = 999999
            f.retrbinary('RETR {}'.format(filename), open(filename, 'wb').write, buf_size)
        except Exception as e:
            msg = u"FTP:读取文件失败, 文件{}在{}中!".format(filename, host)
            logging.info(e)
            os.unlink(filename)
            logging.info(msg)
            raise UserError(msg)
        else:
            os.getcwd()
            # 获取完成后删除ftp中的远程文件
            f.delete(filename)
            f.quit()
            logging.info(u">>>>>>>>>>>>成功下载文件:{},保存在项目根目录!".format(filename))
            return True

    @classmethod
    def up_ftp_server_file(cls, dir_ftp, filename, host, port, username, password):
        """
        上传指定文件到指定ftp
        :param dir_ftp: 目标文件在 ftp 服务器上路径；
        :param filename: 目标文件名；
        :param host: ftp 服务器地址（ip/域名）；
        :param port: ftp 服务器端口号，一般是 21；
        :param username: 登陆 ftp 服务器时的用户名
        :param password: 登陆 ftp 服务器时的密码
        :return boolean
        """
        logging.info(u">>>>>>>>>>>>start上传文件:{}至FTP".format(filename))
        ftp = FTP()
        ftp.set_debuglevel(0)  # 打开调试级别2，显示详细信息;0为关闭调试信息
        ftp.connect(host, port)  # 连接
        ftp.login(username, password)  # 登录，如果匿名登录则用空串代替即可
        ftp.cwd(dir_ftp)  # 选择操作目录
        bufsize = 999999  # 设置缓冲块大小
        file_handler = open(filename, 'rb')  # 以读模式在本地打开文件
        ftp.storbinary('STOR %s' % os.path.basename(filename), file_handler, bufsize)  # 上传文件
        ftp.set_debuglevel(0)
        file_handler.close()
        ftp.quit()
        logging.info(u">>>>>>>>>>>>成功上传文件:{}至FTP".format(filename))
        return True

    @classmethod
    def read_local_file(cls, filename):
        """读取本地文件，返回xml字符串信息
        :param filename: 文件名称（含路径）
        :return string: xml字符串
        """
        import xml.etree.cElementTree as ET
        tree = ET.ElementTree(file=filename)
        root = tree.getroot()
        str_xml = tostring(root, encoding='gbk')
        str_xml = str_xml.replace("<?xml version='1.0' encoding='gbk'?>", '').replace("\n", "").replace("\r\n", "")
        xml_len = '0' + str(len(str_xml))
        i = 0
        while i < 7 - (len(xml_len)):
            xml_len = xml_len + ' '
        str_xml = '{}{}'.format(xml_len, str_xml)
        return str_xml

    @classmethod
    def send_wages_xml(cls, ip, port, xml_str):
        """
        发送代发工资xml信息到前置机
        :param ip:IP地址
        :param port: 端口
        :param xml_str: xml报文
        :return result_xml :结果xml
        """
        logging.debug(xml_str)
        address = (ip, int(port))
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(address)
        except socket.error:
            raise UserError(u"尝试连接到农业银行前置机发生错误！无法连接！")
        client.send(xml_str)
        data = client.recv(9999999)  # 接受响应信息
        data = data.decode('gbk')
        client.close()
        return data

    @classmethod
    def supplement_string_length(cls, old_str, number):
        """
        将字符串的长度转换为指定长度
        :param old_str: 需要生成的字符串
        :param number: 需要生成的长度
        :return: 请求新的字符串
        """
        if old_str:
            str_len = len(old_str)
            i = 0
            while i < (number - str_len):
                old_str = old_str + ' '
                i = i + 1
            return old_str
        else:
            i = 0
            new_str = ''
            while i < number:
                new_str = new_str + ' '
                i = i + 1
            return new_str

    @classmethod
    def supplement_amt_length(cls, amt, number):
        """将金额按照指定长度生成新的字符串"""
        new_amt = Decimal(amt).quantize(Decimal('0.000'))
        new_amt = str(new_amt)
        str_len = len(new_amt)
        i = 0
        while i < (number - str_len):
            new_amt = new_amt + ' '
            i = i + 1
        return new_amt


