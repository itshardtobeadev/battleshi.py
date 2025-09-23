import socket
import threading
import json
import logging
from datetime import datetime

class Ship:
    def __init__(self, name, size, ship_id):
        self.name = name
        self.size = size
        self.id = ship_id
        self.hits = 0
        self.positions = []
    
    def is_sunk(self):
        return self.hits >= self.size

class Player:
    def __init__(self, addr, player_id):
        self.addr = addr
        self.id = player_id
        self.board = [[' ' for _ in range(10)] for _ in range(10)]
        self.ships = []
        self.ready = False
        self.shots_taken = set()
        self.ship_positions = {}  # Mapeia (x,y) -> ship_id
    
    def place_ships(self, ships_data):
        """Coloca navios no tabuleiro do jogador"""
        try:
            # Limpar dados anteriores
            self.ships = []
            self.board = [[' ' for _ in range(10)] for _ in range(10)]
            self.shots_taken = set()
            self.ship_positions = {}
            
            # Definir tipos de navios
            ship_sizes = [5, 4, 3, 3, 2]
            ship_names = ["Porta-aviões", "Encouraçado", "Cruzador", "Submarino", "Destroyer"]
            
            for i, ship_data in enumerate(ships_data):
                size = ship_sizes[i]
                name = ship_names[i]
                positions = ship_data['positions']
                
                # Validar posições
                if not self._validate_ship_placement(positions, size):
                    return False
                
                # Criar navio
                ship = Ship(name, size, i)
                ship.positions = positions
                self.ships.append(ship)
                
                # Marcar no tabuleiro e mapear posições
                for x, y in positions:
                    self.board[x][y] = 'S'
                    self.ship_positions[(x, y)] = ship.id
            
            self.ready = True
            return True
            
        except Exception as e:
            logging.error(f"Erro ao colocar navios: {e}")
            return False
    
    def _validate_ship_placement(self, positions, size):
        """Valida se o posicionamento do navio é válido"""
        # Verificar tamanho
        if len(positions) != size:
            return False
        
        # Verificar se está dentro do tabuleiro
        for x, y in positions:
            if not (0 <= x < 10 and 0 <= y < 10):
                return False
            if self.board[x][y] != ' ':  # Verificar sobreposição
                return False
        
        # Verificar se as posições são consecutivas
        return self._are_positions_consecutive(positions)
    
    def _are_positions_consecutive(self, positions):
        """Verifica se as posições formam uma linha reta consecutiva"""
        if len(positions) <= 1:
            return True
        
        # Verificar horizontal
        row_same = all(pos[0] == positions[0][0] for pos in positions)
        if row_same:
            cols = sorted([pos[1] for pos in positions])
            return all(cols[i] + 1 == cols[i+1] for i in range(len(cols)-1))
        
        # Verificar vertical
        col_same = all(pos[1] == positions[0][1] for pos in positions)
        if col_same:
            rows = sorted([pos[0] for pos in positions])
            return all(rows[i] + 1 == rows[i+1] for i in range(len(rows)-1))
        
        return False
    
    def take_shot(self, x, y):
        """Processa um tiro no tabuleiro do jogador"""
        if (x, y) in self.shots_taken:
            return "repetido", None
        
        self.shots_taken.add((x, y))
        
        if self.board[x][y] == 'S':  # Acertou um navio
            self.board[x][y] = 'X'  # Marcar como acerto
            
            # Encontrar navio atingido
            ship_id = self.ship_positions.get((x, y))
            hit_ship = None
            for ship in self.ships:
                if ship.id == ship_id:
                    ship.hits += 1
                    hit_ship = ship
                    break
            
            if hit_ship and hit_ship.is_sunk():
                # Marcar todas as posições do navio como afundado
                for px, py in hit_ship.positions:
                    self.board[px][py] = 'D'
                return "afundado", hit_ship
            else:
                return "acerto", hit_ship
        else:
            self.board[x][y] = 'O'  # Marcar como água
            return "erro", None
    
    def has_lost(self):
        """Verifica se o jogador perdeu"""
        return all(ship.is_sunk() for ship in self.ships)

class BattleShipServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.players = {}
        self.game_state = "waiting"
        self.current_turn = 1
        self.lock = threading.Lock()
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    def start(self):
        """Inicia o servidor"""
        try:
            self.sock.bind((self.host, self.port))
            logging.info(f"🚀 Servidor BATTLESHI.PY iniciado em {self.host}:{self.port}")
            print(f"🎮 Servidor BATTLESHI.PY rodando em {self.host}:{self.port}")
            print("⏳ Aguardando jogadores...")
            
            self._listen()
            
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar servidor: {e}")
    
    def _listen(self):
        """Escuta por mensagens dos clientes"""
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                threading.Thread(target=self._handle_message, args=(data, addr)).start()
            except Exception as e:
                logging.error(f"❌ Erro ao receber mensagem: {e}")
    
    def _handle_message(self, data, addr):
        """Processa mensagens recebidas dos clientes"""
        try:
            message = json.loads(data.decode())
            msg_type = message.get('type')
            
            with self.lock:
                if msg_type == 'join':
                    self._handle_join(addr, message)
                elif msg_type == 'place_ships':
                    self._handle_place_ships(addr, message)
                elif msg_type == 'shoot':
                    self._handle_shoot(addr, message)
                elif msg_type == 'restart':
                    self._handle_restart(addr)
                    
        except Exception as e:
            logging.error(f"❌ Erro ao processar mensagem: {e}")
    
    def _handle_join(self, addr, message):
        """Lida com jogadores se conectando"""
        if addr in self.players:
            self._send_game_state(addr)
            return
        
        if len(self.players) >= 2:
            self._send_error(addr, "🎮 Jogo cheio. Máximo de 2 jogadores.")
            return
        
        player_id = len(self.players) + 1
        self.players[addr] = Player(addr, player_id)
        
        logging.info(f"🎯 Jogador {player_id} conectado: {addr}")
        
        response = {
            'type': 'join_success',
            'player_id': player_id,
            'message': f"Jogador {player_id} conectado!"
        }
        self._send_to_client(addr, response)
        
        if len(self.players) == 2:
            self.game_state = "placing"
            logging.info("🚀 Dois jogadores conectados. Iniciando posicionamento.")
            self._broadcast({
                'type': 'game_start',
                'message': 'Posicione seus navios!'
            })
    
    def _handle_place_ships(self, addr, message):
        """Lida com posicionamento de navios"""
        if self.game_state != "placing":
            self._send_error(addr, "⏳ Jogo não está na fase de posicionamento")
            return
        
        player = self.players.get(addr)
        if not player:
            self._send_error(addr, "❌ Jogador não encontrado")
            return
        
        ships_data = message.get('ships', [])
        
        if player.place_ships(ships_data):
            logging.info(f"🎯 Jogador {player.id} posicionou {len(ships_data)} navios")
            
            self._send_to_client(addr, {
                'type': 'placement_success',
                'message': 'Navios posicionados! Aguardando oponente...'
            })
            
            # Verificar se ambos estão prontos
            all_ready = all(p.ready for p in self.players.values())
            if all_ready:
                self.game_state = "playing"
                self.current_turn = 1
                logging.info("⚔️ Ambos jogadores prontos. Jogo iniciado!")
                self._broadcast({
                    'type': 'game_begin',
                    'message': 'Jogo iniciado!',
                    'turn': self.current_turn
                })
        else:
            self._send_error(addr, "❌ Posicionamento inválido. Use 'Navios Aleatórios'")
    
    def _handle_shoot(self, addr, message):
        """Lida com tiros dos jogadores"""
        if self.game_state != "playing":
            self._send_error(addr, "⏳ Jogo não está em andamento")
            return
        
        player = self.players.get(addr)
        if not player or player.id != self.current_turn:
            self._send_error(addr, "🎯 Não é sua vez")
            return
        
        x = message.get('x')
        y = message.get('y')
        
        if x is None or y is None or not (0 <= x < 10 and 0 <= y < 10):
            self._send_error(addr, "❌ Coordenadas inválidas")
            return
        
        # Encontrar oponente
        opponent = next(p for p in self.players.values() if p.id != player.id)
        
        # Processar tiro
        result, ship = opponent.take_shot(x, y)
        
        if result == "repetido":
            self._send_error(addr, "🎯 Já atirou nesta posição")
            return
        
        logging.info(f"🎯 Jogador {player.id} atirou em ({x},{y}): {result}")
        
        # Preparar resposta
        response = {
            'type': 'shot_result',
            'x': x,
            'y': y,
            'result': result,
            'ship_name': ship.name if ship else None,
            'ship_size': ship.size if ship else None,
            'shooter': player.id,
            'current_turn': self.current_turn
        }
        
        # Atualizar turno
        if result == "erro":
            self.current_turn = 3 - self.current_turn
            response['current_turn'] = self.current_turn
            response['message'] = "🌊 Água! Vez do oponente."
        elif result == "acerto":
            response['message'] = f"💥 Acertou o {ship.name}!"
        elif result == "afundado":
            response['message'] = f"💀 Afundou o {ship.name}!"
        
        # Verificar fim de jogo
        if opponent.has_lost():
            self.game_state = "finished"
            response['game_over'] = True
            response['winner'] = player.id
            response['message'] = f"🎉 Jogador {player.id} venceu!"
            logging.info(f"🎉 Jogador {player.id} venceu o jogo!")
        
        # Enviar resultado para ambos
        self._broadcast(response)
    
    def _handle_restart(self, addr):
        """Reinicia o jogo"""
        with self.lock:
            for player in self.players.values():
                player.ready = False
                player.board = [[' ' for _ in range(10)] for _ in range(10)]
                player.ships = []
                player.shots_taken = set()
                player.ship_positions = {}
            
            self.game_state = "placing"
            self.current_turn = 1
            
            self._broadcast({
                'type': 'game_restart',
                'message': 'Jogo reiniciado! Posicione navios.'
            })
            logging.info("🔄 Jogo reiniciado")
    
    def _send_to_client(self, addr, message):
        """Envia mensagem para um cliente"""
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            logging.error(f"❌ Erro ao enviar para {addr}: {e}")
    
    def _broadcast(self, message):
        """Envia mensagem para todos os jogadores"""
        for addr in self.players.keys():
            self._send_to_client(addr, message)
    
    def _send_error(self, addr, error_msg):
        """Envia mensagem de erro"""
        self._send_to_client(addr, {'type': 'error', 'message': error_msg})
    
    def _send_game_state(self, addr):
        """Envia estado do jogo para jogador reconectado"""
        player = self.players.get(addr)
        if player:
            self._send_to_client(addr, {
                'type': 'game_state',
                'game_state': self.game_state,
                'player_id': player.id,
                'current_turn': self.current_turn
            })

if __name__ == "__main__":
    server = BattleShipServer()
    server.start()