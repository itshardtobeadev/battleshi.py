# Battleshi.py

Implementação do jogo Batalha Naval em Python, utilizando o protocolo UDP para comunicação entre um servidor e dois clientes.  
O projeto roda em localhost (127.0.0.1), permitindo que dois jogadores disputem uma partida completa através de uma interface gráfica em tkinter. Projeto feito para a disciplina de Redes de Computadores com o professor Dr. Iguatemi Fonseca.

---

## Funcionalidades

- Servidor UDP central:
  - Gerencia conexões (máximo 2 jogadores).
  - Valida o posicionamento dos navios.
  - Controla os turnos dos jogadores.
  - Informa acertos, erros e navios afundados.
  - Encerramento da partida quando um jogador vence.

- Cliente com interface gráfica (tkinter):
  - Tabuleiro do jogador para posicionamento inicial.
  - Tabuleiro do inimigo para ataques.
  - Indicação visual de acertos, erros e navios afundados.
  - Área de status com mensagens do servidor.

- Regras:
  - Tabuleiro 10x10.
  - Navios:
    - Porta-aviões (5 células)  
    - Encouraçado (4 células)  
    - Cruzador (3 células)  
    - Submarino (3 células)  
    - Destroyer (2 células)
  - O jogador continua jogando se acertar; passa a vez se errar.
  - Vitória ao destruir todos os navios inimigos.

---

## Estrutura do projeto

```text
├── server.py   # Servidor UDP e lógica completa do jogo  
└── client.py   # Cliente com interface gráfica (tkinter)
```


---

## Como executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/batalha-naval-udp.git
   cd batalha-naval-udp
   ```
   
2. Inicie o Servidor
   ```bash
   python server.py
   ```

   
3. Em dois terminais separados, inicie os clientes:
   ```bash
   python client.py
   python client.py
   ```

   ---

## Jogando online com Hamachi

Por padrão, o jogo foi feito para rodar em `127.0.0.1` (localhost), mas é possível jogar online com um amigo usando Hamachi.

### Passo 1: Instalar o Hamachi
- Baixe e instale o [LogMeIn Hamachi](https://vpn.net/) em ambos os computadores.

### Passo 2: Criar ou entrar em uma rede
- Um jogador deve criar uma rede no Hamachi (menu Rede > Criar nova rede).  
- O outro jogador deve entrar nessa rede (menu Rede > Entrar em uma rede existente) usando o ID e senha fornecidos.

### Passo 3: Configurar o servidor
- No computador do host (quem criou a rede Hamachi), copie o endereço IPv4 mostrado no Hamachi.  
  - Exemplo: `25.45.123.67`  
- Edite os arquivos `server.py` e `client.py`, substituindo o endereço IP.
  


   


  


