#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# AuditIM - Auditoria de Mensageiros Instantaneos
# Developer: Eduardo Goncalves <egoncalves.arte@gmail.com>
# 2013

#
# LIBS
#

import wx
import pynotify
import time
import utils
from MySQLdb import Connect
import Skype4Py

#
# FUNCOES
#

def Notify(title,message,image): #exibir notificacoes no balao
    notice.update(title,message,image)
    notice.show()
    return

def gerenciaContatos():
	print "gerencia contatos inicio"
	contatos = skype.Friends
	query = "SELECT * FROM contact WHERE user_name = '%s'" % (skype.CurrentUser.Handle)
	conn = Connect(host='auditim.tk', user='db_auditim', passwd='$passW0rD')
	curs = conn.cursor()
	curs.execute('use db_auditim')
	curs.execute(query)
	rows = curs.fetchall()
	for row in rows:
		print "contato no banco de dados: ", row[1]
		for contato in contatos:
			print "contato no Skype: ", contato.Handle
	    		if contato.Handle == row[1]:
				if row[3] == 'False':
		    			contato.IsBlocked = ''
				else:
		    			contato.IsBlocked = 'True'
	print "gerencia contatos fim"

def RunClient(): #pergunta a o usuario se deseja executar o cliente do skype se nao estiver em execucao
    if skype.Client.IsRunning == 0:
        keepRunning = wx.MessageDialog(None, 'Abrir o Skype?','AuditIM', wx.YES_NO | wx.ICON_QUESTION)
        if keepRunning.ShowModal() == wx.ID_YES:
            keepRunning.Destroy()
            Notify('AuditIM','Iniciando o Skype','')
            skype.Client.Start()
            time.sleep(2)
            if skype.Client.IsRunning==1:
                Notify('AuditIM','Skype iniciado, faça login.','')
            time.sleep(2)
        else:
            Notify('Fechando o AuditIM','','')
            exit()

def Attach():
    while skype.AttachmentStatus != 0: #conecta o auditim no skype / fica executando ate o usuario aceitar conectar ao skype
        RunClient() #executa o skype caso o usuario fechar
        try:
            skype.Attach()
            time.sleep(2)
        except Skype4Py.errors.SkypeAPIError:
            time.sleep(2)

def userPLogin():
    Notify('AuditIM','Checando se o usuário: '+skype.CurrentUser.FullName+' tem permissão para utilizar o Skype','')
    conn = Connect(host='auditim.tk', user='db_auditim', passwd='$passW0rD')
    curs = conn.cursor()
    curs.execute('use db_auditim')
    curs.execute('SELECT * FROM user WHERE user_name = %s', (skype.CurrentUser.Handle))
    rows = curs.fetchall()
    if not rows or rows[0][2]=='N':
        Notify('AuditIM','Desculpe, mas o usuário de Skype: "'+skype.CurrentUser.FullName+'" não está autorizado, caso necessário entre em contato com o administrador.','')
        skype.Client.Shutdown() #fecha o Skype, fazendo logoff
        time.sleep(2)
        skype.Client.Start()
        time.sleep(2)
        Notify('AuditIM','Tente utilizar um usuário permitido, caso não funcione entre em contato com o administrador.','')

    #if rows and
def Connection(status):
    userPLogin() #verifica se o usuário logado tem permissão de usar o skype
    Notify('AuditIM','Atenção, essa seção será gravada para fins de auditoria','')
    for contato in skype.Friends: #bloqueia todos os contatos
	contato.IsBlocked = 'True'

    while skype.ConnectionStatus == Skype4Py.conOnline:
	gerenciaContatos()
        time.sleep(10)
    while skype.ConnectionStatus == Skype4Py.conOffline:
        Attach()
        time.sleep(10)

def userStatus(status):
    update = "UPDATE user SET user_status = '%s' WHERE user_name = '%s'" % (skype.CurrentUserStatus,skype.CurrentUser.Handle)
    conn = Connect(host='auditim.tk', user='db_auditim', passwd='$passW0rD')
    curs = conn.cursor()
    curs.execute('use db_auditim')
    curs.execute(update)
    conn.commit()

def handleMessages(msg,status):
    print "handleMessages"
    if status == 'SENT' or status == 'READ':
        conn = Connect(host='auditim.tk', user='db_auditim', passwd='$passW0rD')
        curs = conn.cursor()
        curs.execute('use db_auditim')
        curs.execute('insert into history (user_name, chat_id, chat_name, from_name_user, from_name_display, message_status, message_type, message_body, chat_date, chat_timestamp) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (skype.CurrentUser.Handle, msg.Id, msg.ChatName, msg.FromHandle, msg.FromDisplayName, status, msg.Type, msg.Body, msg.Datetime, msg.Timestamp))
        conn.commit()

#
#
#

app = wx.App()

pynotify.init('AuditIM')
notice = pynotify.Notification('Iniciando o AuditIM', 'AuditIM - Monitora de Mensageiro Instantaneo.','camera-web')
notice.show()

skype = Skype4Py.Skype()
skype.FriendlyName = 'AuditIM'
skype.OnConnectionStatus = Connection
skype.OnMessageStatus = handleMessages
skype.OnUserStatus = userStatus

Attach()
