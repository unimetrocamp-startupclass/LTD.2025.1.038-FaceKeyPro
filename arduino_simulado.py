import tkinter as tk
import time
import threading
import os

class ArduinoSimulado:
    def __init__(self, master):
        self.master = master
        self.master.title("Arduino Simulado")
        self.master.geometry("200x200")

        self.canvas = tk.Canvas(master, width=150, height=150)
        self.canvas.pack(pady=20)

        # LED: círculo inicial (cinza)
        self.led = self.canvas.create_oval(30, 30, 120, 120, fill="gray")

        # Inicia verificação contínua do comando
        self.verificar_comando()

    def verificar_comando(self):
        comando = self.ler_comando()

        if comando:
            if comando == "verde":
                self.canvas.itemconfig(self.led, fill="green")
                print("[LED VERDE] Aceso ✅ (Login OK)")
            elif comando == "vermelho":
                self.canvas.itemconfig(self.led, fill="red")
                print("[LED VERMELHO] Aceso ❌ (Login Falhou)")
            else:
                print(f"[Comando desconhecido] '{comando}'")

            self.limpar_comando()

        # Checa novamente a cada 1 segundo
        self.master.after(1000, self.verificar_comando)

    def ler_comando(self):
        if not os.path.exists("comando.txt"):
            return None
        with open("comando.txt", "r") as f:
            comando = f.read().strip()
        return comando if comando else None

    def limpar_comando(self):
        open("comando.txt", "w").close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoSimulado(root)
    root.mainloop()
