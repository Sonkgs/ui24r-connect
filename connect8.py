import tkinter as tk
from PIL import Image, ImageTk
import socket

# Configuração do socket
HOST = "172.20.4.175"  # IP da mesa de som
PORT = 80

# Criar conexão persistente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
    client.send(("GET /raw HTTP1.1\n\n").encode())  # Mantém a conexão viva
except socket.error as e:
    print(f"Erro ao conectar: {e}")
    client = None  # Evita tentativas se a conexão falhar

def enviar_comando(valor):
    """Envia o valor correto da máscara."""
    if client:
        try:
            comando = f"SETD^mgmask^{valor}\n"
            client.send(comando.encode())
            print(f"Enviando comando: {comando.strip()}")
        except socket.error as e:
            print(f"Erro ao enviar comando: {e}")

def atualizar_mascara():
    """Atualiza o valor da máscara baseado nos botões ativados."""
    valor_mascara = (1 if estado1 else 0) + (2 if estado2 else 0)
    enviar_comando(valor_mascara)

def alternar_mascara1():
    """Alterna estado da Máscara 1 e atualiza a interface."""
    global estado1
    estado1 = not estado1
    botao1.config(image=img_on if estado1 else img_off)
    atualizar_mascara()

def alternar_mascara2():
    """Alterna estado da Máscara 2 e atualiza a interface."""
    global estado2
    estado2 = not estado2
    botao2.config(image=img_on if estado2 else img_off)
    atualizar_mascara()

# Criar a janela
root = tk.Tk()
root.title("Controle de Máscaras")

# Definir tamanho das imagens
tamanho = (100, 100)

# Carregar e redimensionar imagens
img_on = Image.open("on.jpeg").resize(tamanho, Image.LANCZOS)
img_off = Image.open("off.jpeg").resize(tamanho, Image.LANCZOS)

# Converter para formato Tkinter
img_on = ImageTk.PhotoImage(img_on)
img_off = ImageTk.PhotoImage(img_off)

# Estados iniciais
estado1 = False
estado2 = False

# Criar botões
botao1 = tk.Button(root, image=img_off, command=alternar_mascara1,
                   borderwidth=3, relief="solid", cursor="hand2",
                   highlightthickness=2, highlightbackground="black")
botao1.pack(pady=10)

botao2 = tk.Button(root, image=img_off, command=alternar_mascara2,
                   borderwidth=3, relief="solid", cursor="hand2",
                   highlightthickness=2, highlightbackground="black")
botao2.pack(pady=10)

# Fechar conexão ao sair
def fechar_conexao():
    if client:
        client.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", fechar_conexao)  # Fecha a conexão ao sair
root.mainloop()