# Reconhecimento Facial com Banco de Dados

Projeto acadêmico da **Unimetrocamp** que implementa um sistema simples de reconhecimento facial com armazenamento de informações em um banco de dados.

Este sistema pode ser usado para fins de autenticação, controle de presença ou segurança, simulando o funcionamento básico de reconhecimento facial em dispositivos modernos.

## 📁 Estrutura do Projeto

O projeto é composto por **3 arquivos principais**:

### `dataset_creator.py`
Este script é responsável por **criar o conjunto de dados de imagens faciais**. Ele funciona de forma semelhante ao cadastro de rosto em um smartphone — a câmera capta várias imagens do rosto da pessoa e as salva em uma pasta.

### `trainer.py`
Treina o modelo de reconhecimento facial usando os dados criados pelo `dataset_creator.py`. O modelo treinado será usado posteriormente para identificar rostos conhecidos.

### `detector.py`
Este script realiza a **detecção e reconhecimento facial em tempo real**. Quando um rosto cadastrado é detectado, ele mostra o resultado na tela.

## 🧰 Requisitos

Antes de executar o projeto, certifique-se de instalar as dependências:

```bash
pip install opencv-contrib-python
pip install pillow

