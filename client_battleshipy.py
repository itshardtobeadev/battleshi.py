import socket
import json
import threading
import tkinter as tk
from tkinter import messagebox
import random
import math

class PixelArtBattleship:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_addr = ('127.0.0.1', 12345)
        self.player_id = None
        self.game_state = "waiting"
        self.current_turn = None
        self.my_board = [[' ' for _ in range(10)] for _ in range(10)]
        self.opponent_board = [[' ' for _ in range(10)] for _ in range(10)]
        self.ships_placed = False
        
        # Cores retrofuturistas
        self.colors = {
            'bg': '#0a0a12',
            'panel': '#1a1a2e',
            'accent': '#00ffff',
            'accent2': '#ff00ff',
            'text': '#e0e0ff',
            'grid': '#2a2a4a',
            'ship': '#00ff88',
            'hit': '#ff4444',
            'miss': '#4444ff',
            'sunk': '#ffaa00'
        }
        
        self.setup_gui()
        self.connect_to_server()
    
    def setup_gui(self):
        """Configura interface retrofuturista pixelart"""
        self.root = tk.Tk()
        self.root.title("BATTLESHI.PY - RetroFuturist Edition")
        self.root.configure(bg=self.colors['bg'])
        self.root.geometry('900x700')
        
        # Frame principal com estilo cyber
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], relief='flat')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Cabeçalho com efeito pixelart
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'], relief='flat')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Título principal com efeito neon
        title_text = "🚢 BATTLESHI.PY 🚢"
        title_label = tk.Label(header_frame, text=title_text,
                              font=('Courier New', 24, 'bold'),
                              fg=self.colors['accent'],
                              bg=self.colors['bg'],
                              relief='raised',
                              bd=3)
        title_label.pack(pady=5)
        
    
        
        # Painel de status
        self.status_frame = tk.Frame(main_frame, bg=self.colors['panel'],
                                    relief='sunken', bd=2)
        self.status_frame.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(self.status_frame,
                                    text="🔄 CONECTANDO AO SERVIDOR...",
                                    font=('Courier New', 12, 'bold'),
                                    fg=self.colors['text'],
                                    bg=self.colors['panel'])
        self.status_label.pack(pady=8)
        
        # Frame dos tabuleiros
        boards_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        boards_frame.pack(fill='both', expand=True)
        
        # Tabuleiro do jogador
        player_frame = self.create_board_frame(boards_frame, "MEU TABULEIRO", True)
        player_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Tabuleiro do oponente
        opponent_frame = self.create_board_frame(boards_frame, "RADAR INIMIGO", False)
        opponent_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Painel de controle
        self.setup_control_panel(main_frame)
        
        # Legenda pixelart
        self.setup_legend(main_frame)
        
        # Desenhar tabuleiros
        self.draw_boards()
    
    def create_board_frame(self, parent, title, is_player):
        """Cria frame para um tabuleiro"""
        frame = tk.Frame(parent, bg=self.colors['panel'], relief='raised', bd=3)
        
        # Título do tabuleiro
        title_label = tk.Label(frame, text=title,
                              font=('Courier New', 12, 'bold'),
                              fg=self.colors['accent'],
                              bg=self.colors['panel'])
        title_label.pack(pady=5)
        
        # Canvas do tabuleiro
        canvas = tk.Canvas(frame, width=350, height=350,
                          bg=self.colors['bg'], highlightthickness=0)
        canvas.pack(pady=10, padx=10)
        
        if is_player:
            self.player_canvas = canvas
        else:
            self.opponent_canvas = canvas
            canvas.bind('<Button-1>', self.on_opponent_click)
        
        return frame
    
    def setup_control_panel(self, parent):
        """Configura painel de controle"""
        control_frame = tk.Frame(parent, bg=self.colors['panel'],
                               relief='sunken', bd=2)
        control_frame.pack(fill='x', pady=5)
        
        # Botão de navios aleatórios
        self.random_btn = tk.Button(control_frame,
                                   text="🎲 NAVIOS ALEATÓRIOS",
                                   font=('Courier New', 10, 'bold'),
                                   bg=self.colors['accent2'],
                                   fg='black',
                                   relief='raised',
                                   bd=3,
                                   command=self.place_random_ships)
        self.random_btn.pack(side='left', padx=10, pady=5)
        
        # Botão de reinício
        self.restart_btn = tk.Button(control_frame,
                                    text="🔄 REINICIAR JOGO",
                                    font=('Courier New', 10, 'bold'),
                                    bg=self.colors['accent'],
                                    fg='black',
                                    relief='raised',
                                    bd=3,
                                    command=self.restart_game)
        self.restart_btn.pack(side='right', padx=10, pady=5)
        
        # Desabilitar inicialmente
        self.random_btn.config(state='disabled')
        self.restart_btn.config(state='disabled')
    
    def setup_legend(self, parent):
        """Configura legenda pixelart"""
        legend_frame = tk.Frame(parent, bg=self.colors['bg'])
        legend_frame.pack(fill='x', pady=5)
        
        legend_items = [
            ("▓▓", self.colors['ship'], "NAVIO"),
            ("▒▒", self.colors['hit'], "ACERTO"),
            ("░░", self.colors['miss'], "ÁGUA"),
            ("██", self.colors['sunk'], "AFUNDADO")
        ]
        
        for symbol, color, text in legend_items:
            item_frame = tk.Frame(legend_frame, bg=self.colors['bg'])
            item_frame.pack(side='left', padx=10)
            
            symbol_label = tk.Label(item_frame, text=symbol,
                                  font=('Courier New', 12, 'bold'),
                                  fg=color, bg=self.colors['bg'])
            symbol_label.pack(side='left')
            
            text_label = tk.Label(item_frame, text=text,
                                font=('Courier New', 8),
                                fg=self.colors['text'], bg=self.colors['bg'])
            text_label.pack(side='left', padx=(5, 0))
    
    def draw_pixel_rect(self, canvas, x, y, size, color, pixel_size=4):
        """Desenha um retângulo com efeito pixelart"""
        for i in range(size):
            for j in range(size):
                if i == 0 or i == size-1 or j == 0 or j == size-1:
                    canvas.create_rectangle(
                        x + j * pixel_size,
                        y + i * pixel_size,
                        x + (j + 1) * pixel_size,
                        y + (i + 1) * pixel_size,
                        fill=color, outline=color
                    )
    
    def draw_boards(self):
        """Desenha os tabuleiros com estilo pixelart"""
        for canvas, is_player in [(self.player_canvas, True), (self.opponent_canvas, False)]:
            canvas.delete("all")
            
            # Desenhar grade
            cell_size = 30
            grid_color = self.colors['grid']
            
            for i in range(11):
                # Linhas horizontais
                canvas.create_line(40, 40 + i * cell_size, 
                                 40 + 10 * cell_size, 40 + i * cell_size,
                                 width=2, fill=grid_color)
                # Linhas verticais
                canvas.create_line(40 + i * cell_size, 40,
                                 40 + i * cell_size, 40 + 10 * cell_size,
                                 width=2, fill=grid_color)
            
            # Coordenadas
            letters = 'ABCDEFGHIJ'
            for i, letter in enumerate(letters):
                # Letras
                canvas.create_text(25, 40 + i * cell_size + cell_size//2,
                                 text=letter, font=('Courier New', 10, 'bold'),
                                 fill=self.colors['text'])
                # Números
                canvas.create_text(40 + i * cell_size + cell_size//2, 25,
                                 text=str(i+1), font=('Courier New', 10, 'bold'),
                                 fill=self.colors['text'])
            
            # Desenhar conteúdo das células
            board = self.my_board if is_player else self.opponent_board
            for i in range(10):
                for j in range(10):
                    x = 40 + j * cell_size + 2
                    y = 40 + i * cell_size + 2
                    size = cell_size - 4
                    
                    cell_content = board[i][j]
                    if cell_content == 'S' and is_player:  # Navio (só mostra no próprio tabuleiro)
                        self.draw_pixel_rect(canvas, x, y, size//4, self.colors['ship'])
                    elif cell_content == 'X':  # Acerto
                        canvas.create_rectangle(x, y, x + size, y + size,
                                              fill=self.colors['hit'], outline=self.colors['hit'])
                    elif cell_content == 'O':  # Água
                        canvas.create_rectangle(x, y, x + size, y + size,
                                              fill=self.colors['miss'], outline=self.colors['miss'])
                    elif cell_content == 'D':  # Afundado
                        canvas.create_rectangle(x, y, x + size, y + size,
                                              fill=self.colors['sunk'], outline=self.colors['sunk'])
    
    def connect_to_server(self):
        """Conecta ao servidor"""
        try:
            message = {'type': 'join'}
            self.sock.sendto(json.dumps(message).encode(), self.server_addr)
            threading.Thread(target=self.listen_for_messages, daemon=True).start()
        except Exception as e:
            self.show_error(f"Erro de conexão: {e}")
    
    def listen_for_messages(self):
        """Escuta mensagens do servidor"""
        while True:
            try:
                data, _ = self.sock.recvfrom(1024)
                message = json.loads(data.decode())
                self.root.after(0, self.handle_server_message, message)
            except Exception as e:
                print(f"Erro: {e}")
    
    def handle_server_message(self, message):
        """Processa mensagens do servidor"""
        msg_type = message.get('type')
        
        if msg_type == 'join_success':
            self.player_id = message['player_id']
            self.update_status(f"🎮 JOGADOR {self.player_id} CONECTADO")
            
        elif msg_type == 'game_start':
            self.game_state = "placing"
            self.update_status("🚀 POSICIONE SEUS NAVIOS!")
            self.random_btn.config(state='normal')
            
        elif msg_type == 'placement_success':
            self.ships_placed = True
            self.update_status("⏳ AGUARDANDO OPONENTE...")
            self.random_btn.config(state='disabled')
            
        elif msg_type == 'game_begin':
            self.game_state = "playing"
            self.current_turn = message['turn']
            turn_text = "SUA VEZ! ⚡" if self.current_turn == self.player_id else "VEZ DO OPONENTE"
            self.update_status(f"⚔️ {turn_text}")
            self.restart_btn.config(state='normal')
            
        elif msg_type == 'shot_result':
            self.handle_shot_result(message)
            
        elif msg_type == 'error':
            self.show_error(message['message'])
            
        elif msg_type == 'game_restart':
            self.handle_game_restart()
    
    def handle_shot_result(self, message):
        """Processa resultado de tiro"""
        x, y = message['x'], message['y']
        result = message['result']
        shooter = message['shooter']
        self.current_turn = message['current_turn']
        
        # Atualizar tabuleiro apropriado
        if shooter == self.player_id:  # Nosso tiro
            if result == "acerto":
                self.opponent_board[x][y] = 'X'
                status = f"💥 ACERTOU! {message['ship_name']} ATINGIDO!"
            elif result == "afundado":
                self.opponent_board[x][y] = 'D'
                status = f"💀 {message['ship_name']} AFUNDADO!"
            else:  # erro
                self.opponent_board[x][y] = 'O'
                status = "🌊 ÁGUA! VEZ DO OPONENTE"
        else:  # Tiro do oponente
            if result == "acerto":
                self.my_board[x][y] = 'X'
                status = f"💥 OPONENTE ACERTOU SEU {message['ship_name']}!"
            elif result == "afundado":
                self.my_board[x][y] = 'D'
                status = f"💀 SEU {message['ship_name']} FOI AFUNDADO!"
            else:
                self.my_board[x][y] = 'O'
                status = "🌊 OPONENTE ERROU! SUA VEZ! ⚡"
        
        if message.get('game_over'):
            winner = message['winner']
            if winner == self.player_id:
                status = "🎉 VITÓRIA! VOCÊ VENCEU! 🎉"
            else:
                status = "💀 DERROTA! OPONENTE VENCEU! 💀"
            self.show_info("FIM DE JOGO", status)
        
        self.update_status(status)
        self.draw_boards()
    
    def handle_game_restart(self):
        """Reinicia o jogo no cliente"""
        self.my_board = [[' ' for _ in range(10)] for _ in range(10)]
        self.opponent_board = [[' ' for _ in range(10)] for _ in range(10)]
        self.ships_placed = False
        self.game_state = "placing"
        self.update_status("🔄 JOGO REINICIADO! POSICIONE NAVIOS.")
        self.random_btn.config(state='normal')
        self.draw_boards()
    
    def place_random_ships(self):
        """Posiciona navios aleatoriamente"""
        if self.game_state != "placing" or self.ships_placed:
            return
        
        ships_data = []
        ship_sizes = [5, 4, 3, 3, 2]
        temp_board = [[' ' for _ in range(10)] for _ in range(10)]
        
        for size in ship_sizes:
            placed = False
            attempts = 0
            
            while not placed and attempts < 100:
                attempts += 1
                horizontal = random.choice([True, False])
                
                if horizontal:
                    x = random.randint(0, 9)
                    y = random.randint(0, 10 - size)
                else:
                    x = random.randint(0, 10 - size)
                    y = random.randint(0, 9)
                
                # Verificar posição
                can_place = True
                positions = []
                
                for i in range(size):
                    if horizontal:
                        pos_x, pos_y = x, y + i
                    else:
                        pos_x, pos_y = x + i, y
                    
                    if not (0 <= pos_x < 10 and 0 <= pos_y < 10) or temp_board[pos_x][pos_y] != ' ':
                        can_place = False
                        break
                    positions.append([pos_x, pos_y])
                
                if can_place:
                    # Colocar navio
                    for pos_x, pos_y in positions:
                        temp_board[pos_x][pos_y] = 'S'
                    
                    ships_data.append({
                        'positions': positions,
                        'orientation': 'horizontal' if horizontal else 'vertical'
                    })
                    placed = True
        
        # Enviar para servidor
        message = {'type': 'place_ships', 'ships': ships_data}
        self.sock.sendto(json.dumps(message).encode(), self.server_addr)
        
        # Atualizar tabuleiro local
        self.my_board = temp_board
        self.draw_boards()
    
    def on_opponent_click(self, event):
        """Clique no tabuleiro inimigo"""
        if self.game_state != "playing" or self.current_turn != self.player_id:
            return
        
        cell_size = 30
        x = event.x - 40
        y = event.y - 40
        
        if x < 0 or y < 0:
            return
        
        col = x // cell_size
        row = y // cell_size
        
        if 0 <= row < 10 and 0 <= col < 10:
            if self.opponent_board[row][col] not in [' ', 'S']:
                self.show_warning("🎯 Já atirou aqui!")
                return
            
            message = {'type': 'shoot', 'x': row, 'y': col}
            self.sock.sendto(json.dumps(message).encode(), self.server_addr)
    
    def restart_game(self):
        """Solicita reinício"""
        message = {'type': 'restart'}
        self.sock.sendto(json.dumps(message).encode(), self.server_addr)
    
    def update_status(self, text):
        """Atualiza texto de status"""
        self.status_label.config(text=text)
    
    def show_error(self, message):
        """Mostra erro"""
        messagebox.showerror("ERRO", message)
    
    def show_warning(self, message):
        """Mostra aviso"""
        messagebox.showwarning("AVISO", message)
    
    def show_info(self, title, message):
        """Mostra informação"""
        messagebox.showinfo(title, message)
    
    def run(self):
        """Inicia aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    game = PixelArtBattleship()
    game.run()
