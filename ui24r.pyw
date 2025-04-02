# Authors: Sonkgs; ChatGPT; André G. Teuber; jbviola
# Version: Beta 0.9
#
# Aplicativo criado para uso em uma câmara municipal, 
# dando o controle dos microfones do público e dos outros vereadores ao presidente da comissão
# haja vista que querem que o som seja cortado durante a suspensão da comissão e em outros momentos específicos, 
# mas não há respando legal para que um técnico da casa corte o microfone de um vereador
# O único registro formal que temos é de um vereador na tribuna dizendo que: "é inadmissível que um técnico da casa venha a cercear o direito de fala de um vereador"
# 
# Conecta-se à mesa de som Soundcraft UI24R e ativa/desativa as duas primeiras máscaras para desativar grupos de microfones
# 
# TODO: Criar um cronômetro que desative um microfone automaticamente ao fim do tempo inserido
# TODO: Adicionar atualização em tempo real para receber informações da mesa de som

import tkinter as tk
from PIL import Image, ImageTk
import socket
import os

# Função para carregar o IP salvo (caso exista)
def carregar_ip():
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as file:
            return file.read().strip()
    return "172.20.4.175"  # IP padrão caso não haja configuração salva

# Função para salvar o IP no arquivo
def salvar_ip(ip):
    with open("config.txt", "w") as file:
        file.write(ip)

# Carregar o IP da configuração
HOST = carregar_ip()  # Carrega o IP salvo
PORT = 80

# Função para conectar à mesa de som
def conectar_mesa():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))  # HOST já é global, sem necessidade de global aqui
        client.send(("GET /raw HTTP1.1\n\n").encode())  # Mantém a conexão ativa
        return client
    except socket.error as e:
        print(f"Erro ao conectar: {e}")
        return None

def obter_estado_atual():
    # Obtém o estado atual da variável SETD^mgmask^.
    if client:
        try:
            client.send(("GETD^mgmask^\n").encode())  # Solicita apenas mgmask
            resposta = client.recv(131072).decode()
            for linha in resposta.split("\n"):
                print(linha)
                if "SETD^mgmask^" in linha:
                    try:
                        valor = int(linha.split("^")[-1])
                        print(f"Estado atual da máscara: {valor}")
                        return valor
                    except ValueError:
                        pass
        except socket.error as e:
            print(f"Erro ao ler estado atual: {e}")
    return 0  # Valor padrão caso falhe a leitura

def enviar_comando(valor):
    # Envia o valor correto da máscara. 
    if client:
        try:
            comando = f"SETD^mgmask^{valor}\n"
            client.send(comando.encode())
            print(f"Enviando comando: {comando.strip()}")
        except socket.error as e:
            print(f"Erro ao enviar comando: {e}")

def atualizar_interface():
    # Atualiza a interface gráfica de acordo com o estado da máscara.
    global estado1, estado2
    mgmask = obter_estado_atual()

    estado1 = not (mgmask & 1)
    estado2 = not (mgmask & 2)

    botao1.config(image=img1_on if estado1 else img1_off)
    botao2.config(image=img2_on if estado2 else img2_off)

def atualizar_mascara():
    # Atualiza o valor da máscara baseado nos botões.
    valor_mascara = (0 if estado1 else 1) + (0 if estado2 else 2) 
    enviar_comando(valor_mascara)

def alternar_mascara1():
    # Alterna estado da Máscara 1 e atualiza a interface.
    global estado1
    estado1 = not estado1
    botao1.config(image=img1_on if estado1 else img1_off)
    atualizar_mascara()

def alternar_mascara2():
    # Alterna estado da Máscara 2 e atualiza a interface.
    global estado2
    estado2 = not estado2
    botao2.config(image=img2_on if estado2 else img2_off)
    atualizar_mascara()

# Função para abrir a caixa de configuração do IP
def abrir_configuracao():
    # Exibe a caixa de diálogo para o usuário inserir o IP da mesa de som.
    def salvar():
        ip = entry_ip.get()
        salvar_ip(ip)
        global HOST
        HOST = ip
        client = conectar_mesa()  # Reconnecta com o novo IP
        top.destroy()

    # Criar janela de configuração
    top = tk.Toplevel(root)
    top.title("Configuração do IP")
    top.geometry("300x150")

    # Label e Entry para o IP
    label = tk.Label(top, text="Insira o IP da Mesa de Som:")
    label.pack(pady=10)

    entry_ip = tk.Entry(top)
    entry_ip.insert(0, HOST)  # Preenche com o IP atual
    entry_ip.pack(pady=10)

    botao_salvar = tk.Button(top, text="Salvar", command=salvar)
    botao_salvar.pack(pady=10)

# Criar a conexão com a mesa de som
client = conectar_mesa()

# Criar a janela principal
root = tk.Tk()
root.geometry("210x420")  # Tamanho ajustado da janela
root.title("SOM - Sound Obstruction Module")

# Definir tamanho das imagens
tamanho = (160, 160)

# Carregar e redimensionar imagens específicas para cada botão
img1_on = Image.open("on1.jpeg").resize(tamanho, Image.LANCZOS)
img1_off = Image.open("off1.jpeg").resize(tamanho, Image.LANCZOS)

img2_on = Image.open("on2.jpeg").resize(tamanho, Image.LANCZOS)
img2_off = Image.open("off2.jpeg").resize(tamanho, Image.LANCZOS)

# Converter para formato Tkinter
img1_on = ImageTk.PhotoImage(img1_on)
img1_off = ImageTk.PhotoImage(img1_off)

img2_on = ImageTk.PhotoImage(img2_on)
img2_off = ImageTk.PhotoImage(img2_off)

# Criar botões com imagens diferentes
botao1 = tk.Button(root, image=img1_on, command=alternar_mascara1,
                   borderwidth=3, relief="solid", cursor="hand2",
                   highlightthickness=2, highlightbackground="black")
botao1.pack(pady=10)

botao2 = tk.Button(root, image=img2_on, command=alternar_mascara2,
                   borderwidth=3, relief="solid", cursor="hand2",
                   highlightthickness=2, highlightbackground="black")
botao2.pack(pady=10)

# Botão de configuração com a engrenagem
img_gear = Image.open("engrenagem.png").resize((20, 20), Image.LANCZOS)
img_gear = ImageTk.PhotoImage(img_gear)

botao_gear = tk.Button(root, image=img_gear, command=abrir_configuracao,
                       borderwidth=0, highlightthickness=0, relief="flat",
                       cursor="hand2", background="white")
# Alinhando a engrenagem com os outros botões (logo abaixo do segundo botão)
botao_gear.pack(pady=10)  # Usando pack para centralizar com espaço (pady=10)

# Atualizar a interface com o estado real da mesa
atualizar_interface()

# Fechar conexão ao sair
def fechar_conexao():
    if client:
        client.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", fechar_conexao)  # Fecha a conexão ao sair
root.mainloop()
