# Controle de Acesso por Reconhecimento Facial

Este projeto é um sistema de controle de acesso baseado em **reconhecimento facial**, desenvolvido em Python. Ele permite o cadastro e autenticação de moradores utilizando a webcam e registra os acessos em um banco de dados SQLite.

## 📸 Funcionalidades

- Reconhecimento facial em tempo real usando a biblioteca `face_recognition`
- Cadastro de novos moradores com imagem capturada pela câmera
- Registro de tentativas de acesso com data e hora
- Banco de dados SQLite local para armazenar moradores e acessos
- Interface via terminal e exibição de vídeo com `OpenCV`

## 🧰 Requisitos

Certifique-se de ter o Python 3.6+ instalado. As seguintes bibliotecas são necessárias:

```bash
pip install -r requirements
