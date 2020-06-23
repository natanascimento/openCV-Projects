import numpy as np 
import cv2
from center import center

#Capturando o vídeo
cap = cv2.VideoCapture('videoTest.mp4')
#Passando o valor do MOG2
fgbg = cv2.createBackgroundSubtractorMOG2()

#Posição da Linha
posL = 150
offset = 30

xy1 = (20, posL)
xy2 = (300, posL)
#Array para detecção
detects = []

#Dados iniciais para contagem
total = 0
up = 0
down = 0

while 1:
    #Lendo o Frame
    ret, frame = cap.read()
    #Transformando o frame em uma imagem cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Aplicando o MOG2 na imagem vinda do gray
    fgmask = fgbg.apply(gray)
    #Tirando os ruídos da imagem
    retval, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
    #Criando um kernel necessário para rodar uma morfologia (MORPH_ELLIPSE é um array em formato de elipse)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)) 
    #Criando a morfologia com base no OpenCV Docs (opening)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=2)
    #Criando a morfologia com base no OpenCV Docs (dilation)
    dilation = cv2.dilate(opening,kernel,iterations = 7)
    #Criando a morfologia com base no OpenCV Docs (closing)
    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE,kernel, iterations=8)
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
        if int(area) > 2500:
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
                #Se estiver subindo, realizar a contagem
                if detect[c-1][1] < posL and l[1] > posL:
                    detect.clear()
                    up+=1
                    total+=1
                    cv2.line(frame,xy1,xy2,(0,255,0),5)
                    continue
                #Se estiver descendo, realizar a contagem
                if detect[c-1][1] > posL and l[1] < posL:
                    detect.clear()
                    down+=1
                    total+=1
                    cv2.line(frame,xy1,xy2,(0,0,255),5)
                    continue
                if c > 0:
                    cv2.line(frame,detect[c-1],l,(0,0,255),1)

    #Imprimindo o texto superior
    cv2.putText(frame,"TOTAL:"+str(total),(10,20), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
    cv2.putText(frame,"SUBINDO:"+str(up),(10,40), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
    cv2.putText(frame,"DESCENDO:"+str(down),(10,60), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
    #Mostrando as telas
    cv2.imshow("Contagem de Pessoas - Frame", frame)
    cv2.imshow("Contagem de Pessoas - MORPHOLOGY CLOSING", closing)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()