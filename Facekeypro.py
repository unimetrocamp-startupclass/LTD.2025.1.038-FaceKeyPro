import cv2
import face_recognition
import sqlite3
import os
import numpy as np
import time
from datetime import datetime


class Database:
    """Classe responsável pelo gerenciamento do banco de dados"""
    
    def __init__(self, db_name="condominio.db"):
        """Inicializa a conexão com o banco de dados"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.criar_tabelas()
    
    def criar_tabelas(self):
        """Cria as tabelas necessárias se não existirem"""
       
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS moradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            apartamento TEXT NOT NULL,
            bloco TEXT NOT NULL,
            encoding BLOB
        )
        ''')
        
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            morador_id INTEGER,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            autorizado BOOLEAN,
            FOREIGN KEY (morador_id) REFERENCES moradores (id)
        )
        ''')
        self.conn.commit()
    
    def cadastrar_morador(self, nome, apartamento, bloco, encoding):
        """Cadastra um novo morador no banco de dados"""
        encoding_bytes = encoding.tobytes()
        self.cursor.execute('''
        INSERT INTO moradores (nome, apartamento, bloco, encoding)
        VALUES (?, ?, ?, ?)
        ''', (nome, apartamento, bloco, encoding_bytes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def obter_todos_moradores(self):
        """Retorna todos os moradores cadastrados"""
        self.cursor.execute('SELECT id, nome, apartamento, bloco, encoding FROM moradores')
        moradores = []
        for row in self.cursor.fetchall():
            morador_id, nome, apartamento, bloco, encoding_bytes = row
            encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
            moradores.append({
                'id': morador_id,
                'nome': nome,
                'apartamento': apartamento,
                'bloco': bloco,
                'encoding': encoding
            })
        return moradores
    
    def registrar_acesso(self, morador_id, autorizado):
        """Registra uma tentativa de acesso"""
        self.cursor.execute('''
        INSERT INTO acessos (morador_id, autorizado)
        VALUES (?, ?)
        ''', (morador_id, autorizado))
        self.conn.commit()
    
    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        self.conn.close()


class ReconhecimentoFacial:
    """Classe responsável pelo reconhecimento facial"""
    
    def __init__(self, db):
        """Inicializa o sistema de reconhecimento facial"""
        self.db = db
        self.moradores = []
        self.nomes = []
        self.encodings = []
        self.carregar_moradores()
    
    def carregar_moradores(self):
        """Carrega informações dos moradores do banco de dados"""
        self.moradores = self.db.obter_todos_moradores()
        self.nomes = [morador['nome'] for morador in self.moradores]
        self.encodings = [morador['encoding'] for morador in self.moradores]
        print(f"Carregados {len(self.moradores)} moradores do banco de dados")
    
    def cadastrar_novo_morador(self, frame, nome, apartamento, bloco):
        """Cadastra um novo morador usando a imagem atual"""
       
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if len(face_locations) == 0:
            print("Nenhuma face detectada na imagem.")
            return False
        
        if len(face_locations) > 1:
            print("Múltiplas faces detectadas. Por favor, tenha apenas uma pessoa na imagem.")
            return False
        
        
        face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        
        
        morador_id = self.db.cadastrar_morador(nome, apartamento, bloco, face_encoding)
        
       
        self.moradores.append({
            'id': morador_id,
            'nome': nome,
            'apartamento': apartamento,
            'bloco': bloco,
            'encoding': face_encoding
        })
        self.nomes.append(nome)
        self.encodings.append(face_encoding)
        
        print(f"Morador {nome} cadastrado com sucesso!")
        return True
    
    def identificar_pessoa(self, frame):
        """Identifica uma pessoa na imagem e retorna suas informações"""
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            return None, None
        
       
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            
            if len(self.encodings) > 0:
                matches = face_recognition.compare_faces(self.encodings, face_encoding, tolerance=0.6)
                
                if True in matches:
                    
                    face_distances = face_recognition.face_distance(self.encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        morador = self.moradores[best_match_index]
                        
                        
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        
                       
                        texto = f"{morador['nome']} - Bloco {morador['bloco']} Apto {morador['apartamento']}"
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                        cv2.putText(frame, texto, (left + 6, bottom - 6), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                        
                        return frame, morador
                
            
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, "Não Autorizado", (left + 6, bottom - 6), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return frame, None


class ControleAcesso:
    """Classe principal para controle de acesso ao minimercado"""
    
    def __init__(self):
        """Inicializa o sistema de controle de acesso"""
        self.db = Database()
        self.reconhecimento = ReconhecimentoFacial(self.db)
        self.camera = None
        self.modo_cadastro = False
        self.ultimo_acesso = None
        self.tempo_bloqueio = 3  
    
    def iniciar_camera(self, camera_id=0):
        """Inicia a câmera"""
        self.camera = cv2.VideoCapture(camera_id)
        if not self.camera.isOpened():
            print("Erro ao abrir a câmera!")
            return False
        return True
    
    def abrir_porta(self):
        """Simula a abertura da porta"""
        print("\n===== PORTA ABERTA =====")
       
    def enviar_comando(comando):
        with open("comando.txt", "w") as f:
            f.write(comando)
            
    def executar(self):
        """Executa o sistema de controle de acesso"""
        if not self.iniciar_camera():
            return
        
        print("\n=== Sistema de Controle de Acesso por Reconhecimento Facial ===")
        print("Pressione 'q' para sair")
        print("Pressione 'c' para entrar no modo de cadastro")
        print("Pressione 'a' para voltar ao modo de acesso")
        
        while True:
            ret, frame = self.camera.read()
            if not ret:
                print("Erro ao capturar frame da câmera!")
                break
            
           
            frame = cv2.flip(frame, 1)
            
            if self.modo_cadastro:
                
                cv2.putText(frame, "MODO CADASTRO", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "Pressione 's' para salvar", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                
                frame_processado, morador = self.reconhecimento.identificar_pessoa(frame)
                
                if frame_processado is not None:
                    frame = frame_processado
                
                
                tempo_atual = time.time()
                if morador is not None:
                    with open("comando.txt", "w") as f:
                        f.write("verde")
                    if (self.ultimo_acesso is None or 
                        tempo_atual - self.ultimo_acesso > self.tempo_bloqueio):
                        
                        
                        self.db.registrar_acesso(morador['id'], True)
                        self.abrir_porta()
                        self.ultimo_acesso = tempo_atual
                        
                        
                        
                        cv2.putText(frame, "ACESSO AUTORIZADO", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    with open("comando.txt", "w") as f:
                        f.write("vermelho")
                
            
            cv2.imshow('Controle de Acesso - Minimercado', frame)
            
            # print("Pressione uma tecla: \n")
            key = cv2.waitKey(100) & 0xFF
            # print(f"Tecla pressionada: {key}")
            if key == ord('q'):
              
                break
            
            elif key == ord('c'):
               
                self.modo_cadastro = True
                print("\n--- Modo de Cadastro Ativado ---")
            
            elif key == ord('a'):
               
                self.modo_cadastro = False
                print("\n--- Modo de Acesso Ativado ---")
            
            elif key == ord('s') and self.modo_cadastro:
                cv2.putText(frame, "ISIRA SEUS DADOS ABAIXO:", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                nome = input("Nome do morador: ")
                bloco = input("Bloco: ")
                apartamento = input("Apartamento: ")
                
                ret, frame_cadastro = self.camera.read()
                if ret:
                    frame_cadastro = cv2.flip(frame_cadastro, 1)  # Espelha para cadastro
                    if self.reconhecimento.cadastrar_novo_morador(frame_cadastro, nome, apartamento, bloco):
                        print(f"Morador {nome} cadastrado com sucesso!")
                        print("\n=== Sistema de Controle de Acesso por Reconhecimento Facial ===")
                        print("Pressione 'q' para sair")
                        print("Pressione 'c' para entrar no modo de cadastro")
                        print("Pressione 'a' para voltar ao modo de acesso")
                    else:
                        print("Falha ao cadastrar. Tente novamente.")
        
        
        self.camera.release()
        cv2.destroyAllWindows()
        self.db.fechar()



if __name__ == "__main__":
    try:
        sistema = ControleAcesso()
        sistema.executar()
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()