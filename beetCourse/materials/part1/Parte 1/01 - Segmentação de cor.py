

import cv2
import numpy as np


img = cv2.imread("imagens/cores.jpg")  # Converte a imagem para uma Array


lower_range = np.array([0,0,200]) # Limite inferior da cor desejada
upper_range = np.array([10,10,255]) # Limite superior da cor desejada



mask = cv2.inRange(img,lower_range,upper_range)  # Cria máscara a partir dos valores

cv2.imshow('mascara',mask)

resultado = cv2.bitwise_and(img,img, mask=mask) # Segmenta a área da máscara na imagem original

cv2.imshow('imagem',img)  # Exibe imagem de referência
cv2.imshow('mascara',mask)  # Exibe a máscara da cor selecionada
cv2.imshow('resultado',resultado)  # Exibe a máscara da cor selecionada

cv2.waitKey(0) # Aguarda tecla ser pressionada
cv2.destroyAllWindows()  # Fecha todas as janelas



