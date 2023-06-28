import pygame
import os
import webbrowser

window = pygame.display.set_mode((800,800))
pygame.display.set_caption("Chess")

checkboard_image = pygame.image.load(os.path.join("Assets", 'checkboard.png')).convert()
mark_image = pygame.image.load(os.path.join("Assets", 'Mark.png')).convert_alpha()
w_king_image = pygame.image.load(os.path.join("Assets", 'W_King.png')).convert_alpha()
b_king_image = pygame.image.load(os.path.join("Assets", 'B_King.png')).convert_alpha()
w_pawn_image = pygame.image.load(os.path.join("Assets", 'W_Pawn.png')).convert_alpha()
b_pawn_image = pygame.image.load(os.path.join("Assets", 'B_Pawn.png')).convert_alpha()
w_queen_image = pygame.image.load(os.path.join("Assets", 'W_Queen.png')).convert_alpha()
b_queen_image = pygame.image.load(os.path.join("Assets", 'B_Queen.png')).convert_alpha()
w_rook_image = pygame.image.load(os.path.join("Assets", 'W_Rook.png')).convert_alpha()
b_rook_image = pygame.image.load(os.path.join("Assets", 'B_Rook.png')).convert_alpha()
w_bishop_image = pygame.image.load(os.path.join("Assets", 'W_Bishop.png')).convert_alpha()
b_bishop_image = pygame.image.load(os.path.join("Assets", 'B_Bishop.png')).convert_alpha()
w_knight_image = pygame.image.load(os.path.join("Assets", 'W_Knight.png')).convert_alpha()
b_knight_image = pygame.image.load(os.path.join("Assets", 'B_Knight.png')).convert_alpha()
white_win = pygame.image.load(os.path.join("Assets", 'WhiteWin.png')).convert_alpha()
black_win = pygame.image.load(os.path.join("Assets", 'BlackWin.png')).convert_alpha()
stalemate = pygame.image.load(os.path.join("Assets", 'Stalemate.png')).convert_alpha()
insuff_mat = pygame.image.load(os.path.join("Assets", 'InsuffMat.png')).convert_alpha()
main_menu = pygame.image.load(os.path.join("Assets", 'MainMenu.png')).convert_alpha()

class Player:
    def __init__(self, color, king_row, pawn_row):
        self.color = color
        self.pieces = []
        self.king_row = king_row
        self.pawn_row = pawn_row

    def has_moves(self):
        for piece in self.pieces:
            if piece.get_moves():
                return True
        return False

WHITE = Player("W", 7, 6)
BLACK = Player("B", 0, 1)
PLAYERS = (WHITE, BLACK)

class Piece:
    def __init__(self, player, square):
        self.player = player
        self.color = player.color
        self.square = square
        self.is_selected = False
        player.pieces.append(self)

    def get_coords(self):
        coords = (self.square[0]*100+10, self.square[1]*100+10)
        return coords

class King(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.image = w_king_image if self.color == "W" else b_king_image
        player.king = self
        self.has_moved = False

    def can_castle(self):
        i = self.player.king_row
        castles = []
        short = [[6, i], [5, i]]
        long = [[1, i], [2, i], [3, i]]
        if self.has_moved or is_in_check(self.player):
            return castles
        for piece in self.player.pieces:
            if isinstance(piece, Rook) and piece.has_moved == False:
                if piece.square[0] == 0 and all(x not in occ_sqs() for x in long):
                    castles.append("O-O-O")
                elif piece.square[0] == 7 and all(x not in occ_sqs() for x in short):
                    castles.append("O-O")
        return castles
        
    def get_moves(self):
        moves = get_king_moves(self) + self.can_castle()
        return look_for_checks(self, moves)

class Queen(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.image = w_queen_image if self.color == "W" else b_queen_image

    def get_moves(self):
        moves = get_rook_moves(self) + get_bishop_moves(self)
        return look_for_checks(self, moves)

class Rook(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.image = w_rook_image if self.color == "W" else b_rook_image
        self.has_moved = False

    def get_moves(self):
        moves = get_rook_moves(self)
        return look_for_checks(self, moves)

class Bishop(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.image = w_bishop_image if self.color == "W" else b_bishop_image

    def get_moves(self):
        moves = get_bishop_moves(self)
        return look_for_checks(self, moves)

class Knight(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.image = w_knight_image if self.color == "W" else b_knight_image

    def get_moves(self):
        moves = get_knight_moves(self)
        return look_for_checks(self, moves)

class Pawn(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.image = self.image = w_pawn_image if self.color == "W" else b_pawn_image
        self.move_indicator = -1 if self.color == "W" else 1

    def get_moves(self):
        moves = []
        square = self.square
        indic = self.move_indicator
        if [square[0], square[1]+indic] not in occ_sqs():
            moves.append([square[0], square[1]+indic])
            if square[1] == self.player.pawn_row and [square[0], square[1]+2*indic] not in occ_sqs():
                moves.append([square[0], square[1]+2*indic])

        possible_attacks = ([square[0]-1, square[1]+indic], [square[0]+1, square[1]+indic])
        for piece in enemy(self.player).pieces:
            if piece.square in possible_attacks:
                moves.append(piece.square)
        moves = move_fixer(moves, self)
        return look_for_checks(self, moves)
        
def active_pieces():
    return WHITE.pieces + BLACK.pieces

def occ_sqs():
    return [piece.square for piece in active_pieces()]

def enemy(player):
    return BLACK if player == WHITE else WHITE

def spawn_pieces():
    n = [Knight(player, [i, player.king_row]) for i in (1, 6) for player in PLAYERS]
    q = [Queen(player, [3, player.king_row]) for player in PLAYERS]
    b = [Bishop(player, [i, player.king_row]) for i in (2, 5) for player in PLAYERS]
    r = [Rook(player, [i, player.king_row]) for i in (0, 7) for player in PLAYERS]
    k = [King(player, [4, player.king_row]) for player in PLAYERS]
    p = [Pawn(player, [i, player.pawn_row]) for i in range(8) for player in PLAYERS]
    
def move_fixer(moves, piece):
    for move in moves.copy():
            for coord in move:
                if coord not in range(8):
                    moves.remove(move)
                    break
    for element in piece.player.pieces:
            if element.square in moves.copy():
                moves.remove(element.square)
    return moves

def get_king_moves(king):
    moves = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            moves.append([king.square[0]+i, king.square[1]+j])
    moves = move_fixer(moves, king)
    return moves

def get_rook_moves(rook):
    moves = []
    for i in (-1, 1):
        a = rook.square[0]
        while a in range(8):
            a += i
            moves.append([a, rook.square[1]])
            if [a, rook.square[1]] in occ_sqs():
                break          
        b = rook.square[1]
        while b in range(8):
            b += i
            moves.append([rook.square[0], b])
            if [rook.square[0], b] in occ_sqs():
                break 
    return move_fixer(moves, rook)

def get_bishop_moves(bishop):
    moves = []
    for i in (-1, 1):
        for j in (-1, 1):
            a = bishop.square[0]
            b = bishop.square[1]
            while a in range(8) and b in range(8):
                a += i
                b += j
                moves.append([a, b])
                if [a, b] in occ_sqs():
                    break
    return move_fixer(moves, bishop)

def get_knight_moves(knight):
    moves = []
    for i in (-2, 2):
            for j in (-1, 1):
                moves.append([knight.square[0]+i, knight.square[1]+j])
                moves.append([knight.square[0]+j, knight.square[1]+i])
    return move_fixer(moves, knight)

def look_for_checks(piece, moves):
    for move in moves.copy():
        pc, sq = make_move(piece, move)
        if is_in_check(piece.player):
            moves.remove(move)
        if pc == 4:
            piece.square[0] = 4
            sq[0].square[0] = sq[1]
            continue
        piece.square = sq
        if pc:
            enemy(piece.player).pieces.append(pc)
    return moves

def is_in_check(player):
    indic = -1 if player == WHITE else 1
    king = player.king
    king.player.pieces.remove(king)
    for piece in enemy(king.player).pieces:
        if isinstance(piece, (Rook, Queen)):
            if piece.square in get_rook_moves(king):
                king.player.pieces.append(king)
                return True
    for piece in enemy(king.player).pieces:
        if isinstance(piece, (Bishop, Queen)):
            if piece.square in get_bishop_moves(king):
                king.player.pieces.append(king)
                return True
    for piece in enemy(king.player).pieces:
        if isinstance(piece, King):
            if piece.square in get_king_moves(king):
                king.player.pieces.append(king)
                return True
    for piece in enemy(king.player).pieces:
        if isinstance(piece, Knight):
            if piece.square in get_knight_moves(king):
                king.player.pieces.append(king)
                return True
    for piece in enemy(king.player).pieces:
        if isinstance(piece, Pawn):
            if piece.square in ([king.square[0]-1, king.square[1]+indic], [king.square[0]+1, king.square[1]+indic]):
                king.player.pieces.append(king)
                return True
    king.player.pieces.append(king)
    return False

def make_move(piece, square):
    if square == "O-O-O":
        piece.square[0] = 2
        for rook in piece.player.pieces:
            if rook.square[0] == 0:
                print("hi")
                rook.square[0] = 3
                return 4, (rook, 0)
    if square == "O-O":
        piece.square[0] = 6
        for rook in piece.player.pieces:
            if rook.square[0] == 7:
                rook.square[0] = 5
                return 4, (rook, 7)
    remember_piece = None
    for element in enemy(piece.player).pieces:
        if element.square == square:
            element.player.pieces.remove(element)
            remember_piece = element
            break
    remember_square = piece.square
    piece.square = square
    return remember_piece, remember_square

def draw_screen(winner):
    window.blit(checkboard_image, (0, 0))
    if menu:
        window.blit(main_menu, (0, 0))
    for piece in active_pieces():
        window.blit(piece.image, piece.get_coords())
    try:
        for mark in marks:
            if mark == "O-O":
                cd0 = 600
                cd1 = turn.king_row*100
            elif mark == "O-O-O":
                cd0 = 200
                cd1 = turn.king_row*100
            else:
                cd0 = mark[0]*100
                cd1 = mark[1]*100
            window.blit(mark_image, (cd0, cd1))
    except:
        pass
    if winner:
        if winner == WHITE:
            window.blit(white_win, (250, 325))
        elif winner == BLACK:
            window.blit(black_win, (250, 325))
        elif winner == "Stalemate":
            window.blit(stalemate, (250, 325))
        else:
            window.blit(insuff_mat, (250, 325))
    pygame.display.update()

def chess():
    global marks, turn, menu
    selected_piece = False
    turn = WHITE
    winner = None
    menu = True
    game = False
    
    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            while menu:
                start = pygame.Rect(285, 378, 230, 45)
                h2p = pygame.Rect(285, 478, 230, 45)
                quit = pygame.Rect(285, 578, 230, 45)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        menu = False
                        run = False
                    if event.type == pygame.MOUSEBUTTONUP:
                        m_pos = pygame.mouse.get_pos()
                        if start.collidepoint(m_pos):
                            game = True
                            menu = False
                            spawn_pieces()
                        if quit.collidepoint(m_pos):
                            run = False
                            menu = False
                        if h2p.collidepoint(m_pos):
                            webbrowser.open('https://www.chess.com/learn-how-to-play-chess')
                draw_screen(None)

            if game:
                if event.type == pygame.MOUSEBUTTONUP:
                    m_pos = pygame.mouse.get_pos()
                    m_pos = [int(m_pos[0]/100), int(m_pos[1]/100)]

                    if selected_piece:
                        for piece in turn.pieces:
                            if "O-O-O" in marks and m_pos[0] == 2:
                                m_pos = "O-O-O"
                            if "O-O" in marks and m_pos[0] == 6:
                                m_pos = "O-O"
                            if piece == selected_piece and m_pos in marks:
                                make_move(piece, m_pos)
                                if isinstance(piece, (King, Rook)):
                                    piece.has_moved = True
                                if isinstance(piece, Pawn) and m_pos[1] in (0, 7):
                                    piece.player.pieces.remove(piece)
                                    piece = Queen(piece.player, piece.square)
                                turn = enemy(turn)
                                if turn.has_moves() == False:
                                    game = False
                                break

                        selected_piece = False
                        marks = []

                    else:
                        for piece in turn.pieces:
                            if piece.square == m_pos:
                                selected_piece = piece
                                marks = piece.get_moves()
                                break
            elif run:
                if is_in_check(turn):
                    winner = WHITE if turn == BLACK else BLACK
                else:
                    winner = "Stalemate"
                quit = pygame.Rect(370, 420, 50, 50)
                if event.type == pygame.MOUSEBUTTONUP:
                    m_pos = pygame.mouse.get_pos()
                    if quit.collidepoint(m_pos):
                        run = False
        draw_screen(winner)

chess()