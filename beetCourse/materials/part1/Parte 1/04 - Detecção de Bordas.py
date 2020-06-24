import cv2
import numpy as np

cap = cv2.VideoCapture('imagens/chroma1.mp4')


blur = (3,3)  # Cria Tupla para efeito Blur

convolution_matrix = np.array([[1,0,-1],
                               [1,0,-1],
                               [1,0,-1]]) # Cria Matriz de Convolução para Filtro 2D


while True:

    ret,frame = cap.read()  # Captura um frame 


    if not ret:  # Verifica se o vídeo ainda está ativo
        exit()


    filter_2d = cv2.filter2D(frame,-1, convolution_matrix)  # Aplica o filtro da matriz de convolução no frame

    # Wikipedia sobre processamento de imagens - https://en.wikipedia.org/wiki/Kernel_%28image_processing%29

    #cv2.imshow('convolução',filter_2d) # Exibe o resultado da convolução.
    
    frame_copy = frame.copy()  # Copia um frame em outra array

    img_blur = cv2.blur(frame_copy, blur)  # Aplica o efeito Bluer no frame
    # Documentação Opencv Blur: https://docs.opencv.org/master/d4/d13/tutorial_py_filtering.html

    #cv2.imshow('blur',img_blur)




    src_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)  # Converte a imagem borrada com o efeito Blur para tons de cinza.


    kernel_size = 3

    detected_edges = cv2.Canny(src_gray, 50, 150, kernel_size)  # detecta bordas na imagem em tons de cinza com o efeito Canny
    # Documentação Opencv Canny: https://docs.opencv.org/3.4/da/d5c/tutorial_canny_detector.html


    bordas = cv2.cvtColor(detected_edges, cv2.COLOR_GRAY2BGR)  # Converte a imagem de tons de cinza para BGR com o fim de poder concatenar.

    #cv2.imshow('bordas_canny',bordas) # Exibe a imagem com efeito Canny

    #cv2.imshow("Bordas",bordas)
    concat = cv2.vconcat([filter_2d,bordas])  # Concatena as imagens 

    final = cv2.resize(concat, None, fx=0.5,fy=0.5)  # Redimensiona as imagens concatenadas

    cv2.imshow("Filter 2D", final)  # Exibe as imagens concatenadas.


    k = cv2.waitKey(1)  # Aguarda uma tecla ser pressionada (é necessário para visualizar imagem no opencv)

    if k == ord('q'):  # Se a tecla pressionada for a tecla 'q' finaliza a execução
        exit()	
