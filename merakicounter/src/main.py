import cv2
import numpy as np
import mysql.connector
import datetime
import time
from center import center

#configuração da conexão com  o DB
db_connection = mysql.connector.connect(host="databasetest.ctaato9ab42d.us-east-1.rds.amazonaws.com", user="root", passwd="natan5613", database="storeCapacity")
cursor = db_connection.cursor()

#Definindo Tempo
currentDt = datetime.datetime.now()
#Novo Objeto para o tempo
objTime = currentDt.strftime("%d-%m-%Y %H:%M:%S")

#abrindo o video local
cap = cv2.VideoCapture("rtsp://192.168.248.54:9000/live")
#Passando o valor do MOG2
fgbg = cv2.createBackgroundSubtractorMOG2()
#Configurações para a câmera
#Definindo o nome do frame
winName = "Meraki Entrada - Teltec"
# Define o tamanho desejado para a janela
cap_w = 500
cap_h = 300
# Define a janela de exibição das imagens, com tamanho automático
cv2.namedWindow(winName, cv2.WINDOW_AUTOSIZE)
# Posiciona a janela na metade direita do (meu) monitor
cv2.moveWindow(winName, 360, 0)

#Posição da Linha
posL = 170
offset = 30

xy1 = (100, posL)
xy2 = (350, posL)
#Array para detecção
detects = []

#Dados iniciais para contagem
total = 0
up = 0
down = 0

while True:
    #captura o quadro da camera
    ret, frame = cap.read()
    #Caso tenha um problema no retorno ele para o laço
    if not (ret):
        st = time.time()
        cap = cv2.VideoCapture("rtsp://192.168.248.54:9000/live")
        print ("tempo perdido para reinicialização: ",time.time()-st)
        continue
    # Altera o tamanho da imagem para o desejado
    frame = cv2.resize(frame, (cap_w, cap_h))
    #Transformando o frame em uma imagem cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Aplicando o MOG2 na imagem vinda do gray
    fgmask = fgbg.apply(gray)
    #Tirando os ruídos da imagem
    retval, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
    #Criando um kernel necessário para rodar uma morfologia (MORPH_ELLIPSE é um array em formato de elipse)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)) 
    #Criando a morfologia com base no OpenCV Docs (opening)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=5)
    #Criando a morfologia com base no OpenCV Docs (dilation)
    dilation = cv2.dilate(opening,kernel,iterations=7)
    #Criando a morfologia com base no OpenCV Docs (closing)
    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE,kernel, iterations=10)
    #Criando os contornos e hierarquias
    contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #Adicionando a linha para análise de fluxo
    cv2.line(frame,xy1,xy2,(255,0,0),3)
    #Adicionado linha para 30px superior
    cv2.line(frame,(xy1[0],posL-offset),(xy2[0], posL-offset),(255,255,0),2)
    #Adicionando linha para 30px abaixo da geral
    cv2.line(frame,(xy1[0],posL+offset),(xy2[0], posL+offset),(255,255,0),2)
    #Contador para diferenciar as pessoas
    i = 0
    #Percorendo o array do contorno
    for cntrs in contours:
        #Calculando X, Y, a largura e a altura
        (x,y,w,h) = cv2.boundingRect(cntrs)
        #Calculando a área
        area = cv2.contourArea(cntrs)
        #Criando um filtro da área
        if int(area) > 2000:
            #Calculando o centro do retangulo
            centro = center(x,y,w,h)
            #Definindo o id da pessoa com base na quantidade de pessoas na imagem
            cv2.putText(frame, str(i),(x+5, y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,255,255),2)
            #Circulo no meio do quadrado
            cv2.circle(frame, centro, 4,(0,0,255), -1)
            #Retangulo ao redor do objeto
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

            if len(detects) <= i:
                detects.append([])
            if centro[1] >  posL-offset and centro[1] < posL+offset:
                detects[i].append(centro)
            else:
                detects[i].clear()
            #Passando um valor, caso exista algo na imagem
            i += 1
    #Verificar o numero contornos
    if len(contours) == 0:
        detects.clear()
    else:
        #Percorrer a lista de detecção
        for detect in detects:
            for (c,l) in enumerate(detect):
                #Se estiver saindo, realizar a contagem
                if detect[c-1][1] < posL and l[1] > posL:
                    detect.clear()
                    up+=1
                    total-=1
                    cv2.line(frame,xy1,xy2,(0,255,0),5)
                    sqltotal = "INSERT INTO storeCapacity.fluxo (name, status, time) VALUES (%s, %s,%s)"
                    totalNow = ('Total',total,objTime)
                    cursor.execute(sqltotal,totalNow)
                    db_connection.commit()
                    continue
                #Se estiver entrando, realizar a contagem
                if detect[c-1][1] > posL and l[1] < posL:
                    detect.clear()
                    down+=1
                    total+=1
                    cv2.line(frame,xy1,xy2,(0,0,255),5)
                    sqltotal = "INSERT INTO storeCapacity.fluxo (name, status, time) VALUES (%s, %s,%s)"
                    totalNow = ('Total',total,objTime)
                    cursor.execute(sqltotal,totalNow)
                    db_connection.commit()
                    continue
                if c > 0:
                    cv2.line(frame,detect[c-1],l,(0,0,255),1)

    #Imprimindo o texto superior
    cv2.putText(frame,"TOTAL:"+str(total),(10,20), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
    cv2.putText(frame,"Sairam:"+str(up),(10,40), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
    cv2.putText(frame,"Entraram:"+str(down),(10,60), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
    #Mostrando as telas
    cv2.imshow(winName, frame)

    # Aguarda o pressionamento de uma tecla ou 1 milisegundos
    k = cv2.waitKey(1)
    if k == ord('q') or k == ord('Q') or k == 27:
        break

db_connection.close()
#Realizar release da captura
cap.release()
cv2.destroyAllWindows()