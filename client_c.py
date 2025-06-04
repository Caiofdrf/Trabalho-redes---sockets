import socket
import threading
import pygame
import sys

pygame.init()

HOST = "192.168.120.219"
PORT = 2077
msg_max_len = 1024

WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

# IPv4 e TCP
player = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

board_lock = threading.Lock()

class chessPiece:
    def __init__(self, color, type, image):
        self.color = color
        self.type = type
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (SQUARE_SIZE, SQUARE_SIZE))
        self.has_moved = False

# Tabuleiro global: 8x8 de instâncias de chessPiece ou None
board = [[None for _ in range(8)] for _ in range(8)]

current_player = 'white'
selected_piece = None
selected_pos = None

def init_board():
    with board_lock:
        # Put pawns
        for col in range(8):
            board[1][col] = chessPiece('black', 'pawn', 'pieces_images/black_pawn.png')
            board[6][col] = chessPiece('white', 'pawn', 'pieces_images/white_pawn.png')

        # Put Rooks
        board[0][0] = board[0][7] = chessPiece('black', 'rook', 'pieces_images/black_rook.png')
        board[7][0] = board[7][7] = chessPiece('white', 'rook', 'pieces_images/white_rook.png')

        # Put Knights
        board[0][1] = board[0][6] = chessPiece('black', 'knight', 'pieces_images/black_knight.png')
        board[7][1] = board[7][6] = chessPiece('white', 'knight', 'pieces_images/white_knight.png')

        # Put Bishops
        board[0][2] = board[0][5] = chessPiece('black', 'bishop', 'pieces_images/black_bishop.png')
        board[7][2] = board[7][5] = chessPiece('white', 'bishop', 'pieces_images/white_bishop.png')

        # Put Queens
        board[0][3] = chessPiece('black', 'queen', 'pieces_images/black_queen.png')
        board[7][3] = chessPiece('white', 'queen', 'pieces_images/white_queen.png')

        # Put Kings
        board[0][4] = chessPiece('black', 'king', 'pieces_images/black_king.png')
        board[7][4] = chessPiece('white', 'king', 'pieces_images/white_king.png')

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen,color,(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    if selected_pos:
        pygame.draw.rect(screen,YELLOW,(selected_pos[1] * SQUARE_SIZE,selected_pos[0] * SQUARE_SIZE,SQUARE_SIZE, SQUARE_SIZE))

def draw_piece():
    with board_lock:
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece:
                    screen.blit(piece.image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def get_valid_moves(piece, row, col):
    with board_lock:
        snapshot = [linha[:] for linha in board]

    moves = []
    if piece.type == 'pawn':
        direction = -1 if piece.color == 'white' else 1

        # Moves forward
        if 0 <= row + direction < 8 and snapshot[row + direction][col] is None:
            moves.append((row + direction, col))
            if ((piece.color == 'white' and row == 6) or
                (piece.color == 'black' and row == 1)):
                if snapshot[row + 2 * direction][col] is None:
                    moves.append((row + 2 * direction, col))

        # Takes piece
        for dc in (-1, 1):
            nr, nc = row + direction, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if snapshot[nr][nc] and snapshot[nr][nc].color != piece.color:
                    moves.append((nr, nc))

    elif piece.type == 'rook':
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if snapshot[r][c] is None:
                    moves.append((r, c))
                elif snapshot[r][c].color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

    elif piece.type == 'knight':
        for dr, dc in ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)):
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if snapshot[r][c] is None or snapshot[r][c].color != piece.color:
                    moves.append((r, c))

    elif piece.type == 'bishop':
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if snapshot[r][c] is None:
                    moves.append((r, c))
                elif snapshot[r][c].color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

    elif piece.type == 'queen':
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if snapshot[r][c] is None:
                    moves.append((r, c))
                elif snapshot[r][c].color != piece.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc

    elif piece.type == 'king':
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if snapshot[r][c] is None or snapshot[r][c].color != piece.color:
                        moves.append((r, c))

    return moves

def is_check(color):
    with board_lock:
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p.color == color and p.type == 'king':
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        if king_pos is None:
            return False

        snapshot = [linha[:] for linha in board]

    for r in range(8):
        for c in range(8):
            p = snapshot[r][c]
            if p and p.color != color:
                if king_pos in get_valid_moves(p, r, c):
                    return True
    return False

def is_game_over():
    with board_lock:
        snapshot = [linha[:] for linha in board]
        player_color = current_player

    for r in range(8):
        for c in range(8):
            p = snapshot[r][c]
            if p and p.color == player_color:
                valid_moves = get_valid_moves(p, r, c)
                for mv in valid_moves:
                    temp_board = [linha[:] for linha in snapshot]
                    temp_board[mv[0]][mv[1]] = p
                    temp_board[r][c] = None

                    if not _would_be_in_check(temp_board, player_color):
                        return False
    return True

def _would_be_in_check(temp_board, color):
    king_pos = None
    for r in range(8):
        for c in range(8):
            p = temp_board[r][c]
            if p and p.color == color and p.type == 'king':
                king_pos = (r, c)
                break
        if king_pos:
            break

    if not king_pos:
        return False

    for r in range(8):
        for c in range(8):
            p = temp_board[r][c]
            if p and p.color != color:
                if king_pos in get_valid_moves(p, r, c):
                    return True
    return False

def handle_click(pos):
    global selected_piece, selected_pos, current_player
    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE

    with board_lock:
        piece = board[row][col]

    if selected_piece is None:
        if piece and piece.color == current_player:
            selected_piece = piece
            selected_pos = (row, col)
    else:
        if (row, col) in get_valid_moves(selected_piece,selected_pos[0],selected_pos[1]):
            with board_lock:
                board[row][col] = selected_piece
                board[selected_pos[0]][selected_pos[1]] = None
                selected_piece.has_moved = True

                # Promove peão se necessário
                if selected_piece.type == 'pawn' and (row == 0 or row == 7):
                    cor = selected_piece.color
                    board[row][col] = chessPiece(cor, 'queen',f'pieces_images/{cor}_queen.png')

                current_player = 'black' if current_player == 'white' else 'white'

            if is_game_over():
                if is_check(current_player):
                    print(f"Checkmate, {current_player.capitalize()} perdeu.")
                else:
                    print("Stalemate!")

        selected_piece = None
        selected_pos = None

        send_box = create_box()
        send_current_player()
        send_board(send_box)

def create_box():
    with board_lock:
        snapshot = [linha[:] for linha in board]

    box = ""
    for r in range(8):
        for c in range(8):
            peca = snapshot[r][c]
            if peca is None:
                box += "n"
            else:
                if peca.type == 'pawn':
                    box += "p" if peca.color == 'white' else "P"
                elif peca.type == 'knight':
                    box += "c" if peca.color == 'white' else "C"
                elif peca.type == 'bishop':
                    box += "b" if peca.color == 'white' else "B"
                elif peca.type == 'rook':
                    box += "r" if peca.color == 'white' else "R"
                elif peca.type == 'queen':
                    box += "q" if peca.color == 'white' else "Q"
                elif peca.type == 'king':
                    box += "k" if peca.color == 'white' else "K"
                else:
                    box += "n"
    return box

def send_current_player():
    msg = "CURRENT:" + current_player + "\n"
    try:
        player.send(msg.encode())
    except Exception as e:
        print("erro ao enviar CURRENT:", e)

def send_board(txt_box):
    if not txt_box or len(txt_box) != 64:
        print("Erro: tabuleiro inválido para enviar:", txt_box)
        return
    msg = "BOARD:" + txt_box + "\n"
    try:
        player.send(msg.encode())
    except Exception as e:
        print("erro ao enviar BOARD:", e)

def receive_table():
    global current_player, board
    while True:
        try:
            data = player.recv(msg_max_len)
            if not data:
                player.close()
                break

            table = data.decode('utf-8').strip()
            if table.startswith("CURRENT:"):
                current_player = table.split(":", 1)[1].strip()

            elif table.startswith("BOARD:"):
                payload = table[len("BOARD:"):].strip()
                if len(payload) != 64:
                    print("ERRO: payload inesperado:", repr(payload))
                    continue

                n_board = [[None for _ in range(8)] for _ in range(8)]
                i = 0
                for r in range(8):
                    for c in range(8):
                        char = payload[i]
                        if char == "n":
                            n_board[r][c] = None
                        elif char == "p":
                            n_board[r][c] = chessPiece("white", "pawn", "pieces_images/white_pawn.png")
                        elif char == "P":
                            n_board[r][c] = chessPiece("black", "pawn", "pieces_images/black_pawn.png")
                        elif char == "c":
                            n_board[r][c] = chessPiece("white", "knight", "pieces_images/white_knight.png")
                        elif char == "C":
                            n_board[r][c] = chessPiece("black", "knight", "pieces_images/black_knight.png")
                        elif char == "b":
                            n_board[r][c] = chessPiece("white", "bishop", "pieces_images/white_bishop.png")
                        elif char == "B":
                            n_board[r][c] = chessPiece("black", "bishop", "pieces_images/black_bishop.png")
                        elif char == "r":
                            n_board[r][c] = chessPiece("white", "rook", "pieces_images/white_rook.png")
                        elif char == "R":
                            n_board[r][c] = chessPiece("black", "rook", "pieces_images/black_rook.png")
                        elif char == "q":
                            n_board[r][c] = chessPiece("white", "queen", "pieces_images/white_queen.png")
                        elif char == "Q":
                            n_board[r][c] = chessPiece("black", "queen", "pieces_images/black_queen.png")
                        elif char == "k":
                            n_board[r][c] = chessPiece("white", "king", "pieces_images/white_king.png")
                        elif char == "K":
                            n_board[r][c] = chessPiece("black", "king", "pieces_images/black_king.png")
                        else:
                            n_board[r][c] = None
                        i += 1

                # Substitui o board inteiro dentro do lock
                with board_lock:
                    board = n_board

        except Exception as e:
            print("erro ao receber tabuleiro:", e)
            try:
                player.close()
            except:
                pass
            break

def main():
    try:
        player.connect((HOST, PORT))
    except Exception as e:
        print("falha ao conectar ao servidor:", e)
        sys.exit(1)

    init_board()
    threading.Thread(target=receive_table, daemon=True).start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    player.close()
                except:
                    pass
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(pygame.mouse.get_pos())
        draw_board()
        draw_piece()
        pygame.display.flip()

if __name__ == "__main__":
    main()
