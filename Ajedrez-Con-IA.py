#M ///////////////////////////////////////////////////////////////////////
import pygame #manejar imagenes,audios,clicks,texto
import chess #logica del ajedrez (reglas, movimientos)
import chess.engine #comunicarse con stockfish
import os #definir la ubicacion de Stockfish
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
# CONFIGURACIÓN para el tamaño y colores del tablero
BOARD_WIDTH = 640
BOARD_HEIGHT = 640
EXTRA_WIDTH = 240
WIDTH = BOARD_WIDTH + EXTRA_WIDTH
HEIGHT = BOARD_HEIGHT + 40  
SQUARE_SIZE = BOARD_WIDTH // 8
WHITE = (245, 245, 220)
BLACK = (119, 148, 85)
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
# Ruta al ejecutable Stockfish
STOCKFISH_PATH = os.path.join("C:\\Users\\youll\\OneDrive\\Desktop\\UDLA\II SEMESTRE\\Programacion\\Ajedres_Con_IA_Proyecto_Final\\stockfish", "stockfish-windows-x86-64-avx2.exe")
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
# Se crea un diccionario, para guardar las imagenes
PIECE_IMAGES = {}
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
# Función donde obtiene las imagenes de la carpeta images
def load_images():
    #Diccionario de las imagenes, las carga
    piece_symbols = {
        'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
        'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
    }
    #Carga, redimensiona cada imagen y luego las guarda
    for symbol, filename in piece_symbols.items():
        PIECE_IMAGES[symbol] = pygame.transform.scale(
            pygame.image.load(f"images/{filename}.svg"),
            (SQUARE_SIZE, SQUARE_SIZE)
        )
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
# Función para dibujar el tablero visualmente
def draw_board(screen, board, selected_square=None):
    # Dibujar el botón de rendición
    button_font = pygame.font.SysFont(None, 30)
    surrender_btn = pygame.Rect(BOARD_WIDTH + 40, 100, 160, 40)
    pygame.draw.rect(screen, (200, 0, 0), surrender_btn)
    text = button_font.render("RENDIRSE", True, (255, 255, 255))
    screen.blit(text, (surrender_btn.x + 20, surrender_btn.y + 5))

    # Mostrar piezas comidas
    captured_font = pygame.font.SysFont(None, 20)
    screen.blit(captured_font.render("Blancas comidas:", True, (255, 255, 255)), (BOARD_WIDTH + 40, 160))
    #Agarra la imagen de la que se la comieron y la carga enlaparte de piezas comidas
    for i, piece in enumerate(white_captured[-10:]):  
        img = pygame.transform.scale(PIECE_IMAGES[piece], (25, 25))
        screen.blit(img, (BOARD_WIDTH + 40 + (i % 5) * 24, 180 + (i // 5) * 24))
    screen.blit(captured_font.render("Negras comidas:", True, (255, 255, 255)), (BOARD_WIDTH + 40, 240))
    for i, piece in enumerate(black_captured[-10:]):
        img = pygame.transform.scale(PIECE_IMAGES[piece], (25, 25))
        screen.blit(img, (BOARD_WIDTH + 40 + (i % 5) * 24, 260 + (i // 5) * 24))
    
    #Colores de las casillas del tablero predefinidas
    colors = [WHITE, BLACK]

    # Verificar si el rey está en jaque con python_chess
    in_check = board.is_check()
    check_square = None
    if in_check:
        king_square = board.king(board.turn)
        check_square = king_square

    # Dibujar el tablero y marcar el jaque
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            color = colors[(row + col) % 2]
            # Colorea el rey en jaque
            if square == check_square:
                color = (255, 0, 0)
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    #Dibujar las piezas
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            screen.blit(PIECE_IMAGES[piece.symbol()], pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    #Dibujar correctamente los ejes del tablero (letras y números). 
    font = pygame.font.SysFont(None, 20)
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    
    # Dibujar letras (a-h) en la parte inferior
    for i, letter in enumerate(letters):
        text = font.render(letter, True, (255, 255, 255))
        x = i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_width() // 2
        y = HEIGHT - 18
        screen.blit(text, (x, y))

    # Dibujar números (1-8) a la izquierda
    for i in range(8):
        number = str(8 - i)
        text = font.render(number, True, (0, 0, 0))
        x = 5  
        y = i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_height() // 2
        screen.blit(text, (x, y))
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
# Función para ver los movimiento legales que podemos hacer
def draw_legal_moves(screen, legal_moves):
    #Recorre cada destino y en donde el movimiento es legal dibuja un circulo
    for square in legal_moves:
        col = square % 8
        row = 7 - square // 8
        center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
        pygame.draw.circle(screen, (0, 255, 0), center, 10) 
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
#  Convertir coordenadas de mouse para asi mover las fichas
def get_square(pos):
    x, y = pos
    if x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
        return None  # clic fuera del tablero no hce nd
    col = x // SQUARE_SIZE
    row = 7 - (y // SQUARE_SIZE)
    return chess.square(col, row)
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
# Función para hacer el movimiento de arrastre en las piezas
def animate_move(screen, board, piece_symbol, start_square, end_square):
    #Obtener fila y columna de origen y destino
    start_col = chess.square_file(start_square)
    start_row = 7 - chess.square_rank(start_square)
    end_col = chess.square_file(end_square)
    end_row = 7 - chess.square_rank(end_square)
    #Definir la cantidad de pasos de animación
    steps = 10
    #Bucle para animar el movimiento
    for i in range(1, steps + 1):
        draw_board(screen, board)  # Redibuja el tablero sin mover la pieza
        t = i / steps
        x = (1 - t) * start_col + t * end_col
        y = (1 - t) * start_row + t * end_row
        screen.blit(#Dibujar la pieza en su posición intermedia
            PIECE_IMAGES[piece_symbol],
            pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        )
        #Mostrar en pantalla y esperar un poco
        pygame.display.flip()
        pygame.time.wait(20)
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
#Funcion para dar estilo al menu y crear el menu
def show_start_menu(screen):
    #Inicialización de fuentes y reloj
    pygame.font.init()
    title_font = pygame.font.SysFont("arial", 48)
    option_font = pygame.font.SysFont("arial", 32)
    clock = pygame.time.Clock()
    #Variables para las opciones seleccionadas por defecto
    selected_color = "white"
    difficulty = 3
    time_minutes = 5
    start_button = pygame.Rect(380, 500, 200, 50)
    #Bucle infinito para mantener el menú visible 
    while True:
        screen.fill((0, 0, 0))

        # Título
        title_text = title_font.render("AJEDREZ vs STOCKFISH", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))

        # Selección de color
        color_text = option_font.render("Elige tu color:", True, (255, 255, 255))
        screen.blit(color_text, (100, 120))
        white_btn = pygame.Rect(100, 160, 150, 40)
        black_btn = pygame.Rect(270, 160, 150, 40)
        pygame.draw.rect(screen, (160, 32, 240) if selected_color == "white" else (100, 100, 100), white_btn)
        pygame.draw.rect(screen, (160, 32, 240) if selected_color == "black" else (100, 100, 100), black_btn)
        screen.blit(option_font.render("Blancas", True, (255, 255, 255)), (white_btn.x + 20, white_btn.y + 5))
        screen.blit(option_font.render("Negras", True, (255, 255, 255)), (black_btn.x + 20, black_btn.y + 5))

        # Nivel de dificultad
        screen.blit(option_font.render("Dificultad (1-5):", True, (255, 255, 255)), (100, 230))
        for i in range(1, 6):
            btn = pygame.Rect(100 + (i-1)*60, 270, 50, 40)
            color = (160, 32, 240) if i == difficulty else (100, 100, 100)
            pygame.draw.rect(screen, color, btn)
            screen.blit(option_font.render(str(i), True, (0, 0, 0)), (btn.x + 15, btn.y + 5))
            
        # Tiempo de juego
        screen.blit(option_font.render("Tiempo por jugador (min):", True, (255, 255, 255)), (100, 340))
        for i, t in enumerate([3, 5, 10, 15]):
            btn = pygame.Rect(100 + i * 60, 380, 50, 40)
            color = (128, 0, 128) if t == time_minutes else (100, 100, 100)
            pygame.draw.rect(screen, color, btn)
            screen.blit(option_font.render(str(t), True, (0, 0, 0)), (btn.x + 12, btn.y + 5))

        # Botón de inicio
        pygame.draw.rect(screen, (75, 0, 130), start_button)
        screen.blit(option_font.render("Iniciar Partida", True, (255, 255, 255)),
                    (start_button.x + 10, start_button.y + 10))
        
        #Actualizar pantalla y controlar FPS
        pygame.display.flip()
        clock.tick(60)
        
        # Aqui es para ver onde eta preionando el mouse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # Clic en los botones de blanco o negro
                if white_btn.collidepoint(pos):
                    selected_color = "white"
                elif black_btn.collidepoint(pos):
                    selected_color = "black"
                # Clic en los botones de dificultad
                for i in range(1, 6):
                    btn = pygame.Rect(100 + (i-1)*60, 270, 50, 40)
                    if btn.collidepoint(pos):
                        difficulty = i
                # Clic en los botones de tiempo
                for i, t in enumerate([3, 5, 10, 15]):
                    btn = pygame.Rect(100 + i * 60, 380, 50, 40)
                    if btn.collidepoint(pos):
                        time_minutes = t

                # Verfica si presionamos iniciar partida
                if start_button.collidepoint(pos):
                    return selected_color == "white", difficulty, time_minutes
#M ///////////////////////////////////////////////////////////////////////

#M ///////////////////////////////////////////////////////////////////////
# Variables o listas donde se registraran datos
white_captured = [] #Blanca capturadas
black_captured = [] #Negras capturadas
move_log = [] #Los movimientos se van air guardando
selected_square = None #Guarda donde selecciona el jugaro mover pieza
legal_moves = [] #La lista de movimientos legales 
#M ///////////////////////////////////////////////////////////////////////

# Funcion principal
def main():
    #Inicializa el "programa" que nos permite dibujar 
    pygame.init()

    # Para poner el sonido al mover las piezas 
    pygame.mixer.init()
    move_sound = pygame.mixer.Sound("sounds/pum.mp3")

    # Para mostrar la pantalla
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ajedrez vs Stockfish")
    clock = pygame.time.Clock()
    
    # Mostrar menú gráfico para elegir color, dificultad y tiempo
    player_is_white, level, time_minutes = show_start_menu(screen)
    
     # Inicializar tiempos 
    player_time = time_minutes * 60 
    engine_time = time_minutes * 60
    last_tick = pygame.time.get_ticks()

    # Cargar las imágenes
    load_images()
    
    # Inicializar el tablero
    board = chess.Board()

    # Iniciar el motor o la IA "Stockfish"
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    stockfish_thinking_time = 0.1 * level

    # Aqui si escojimos jugar con negras la IA empieza a jugar
    if not player_is_white:
        result = engine.play(board, chess.engine.Limit(time=stockfish_thinking_time))
        board.push(result.move)
        move_sound.play()

    # Aquí empieza el bucle principal del juego
    selected_square = None
    running = True
    
    while running:
        screen.fill(pygame.Color("black"))
        # Calcular tiempo transcurrido desde el último frame
        now = pygame.time.get_ticks()
        delta = (now - last_tick) / 1000 
        last_tick = now

        # Restar el tiempo solo al jugador que está pensando
        if board.turn == (chess.WHITE if player_is_white else chess.BLACK):
            player_time -= delta
        else:
            engine_time -= delta

        if player_time <= 0:
            msg = "¡Tiempo agotado! Gana Stockfish"
            running = False
        elif engine_time <= 0:
            msg = "¡Stockfish se quedó sin tiempo! ¡Ganas!"
            running = False

        # Mostrar mensaje final si se terminó por tiempo
        if not running:
            font = pygame.font.SysFont(None, 60)
            text = font.render(msg, True, (255, 0, 0))
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, rect)
            pygame.display.flip()
            pygame.time.wait(4000)
            continue

        draw_board(screen, board, selected_square)
        if selected_square is not None:
            draw_legal_moves(screen, legal_moves)
        
        # Mostrar relojes
        clock_font = pygame.font.SysFont(None, 28)

        def format_time(seconds):
            minutes = int(seconds) // 60
            sec = int(seconds) % 60
            return f"{minutes:02}:{sec:02}"

        screen.blit(clock_font.render("Jugador:", True, (255, 255, 255)), (BOARD_WIDTH + 40, 20))
        screen.blit(clock_font.render(format_time(player_time), True, (255, 255, 255)), (BOARD_WIDTH + 140, 20))

        screen.blit(clock_font.render("Stockfish:", True, (255, 255, 255)), (BOARD_WIDTH + 40, 50))
        screen.blit(clock_font.render(format_time(engine_time), True, (255, 255, 255)), (BOARD_WIDTH + 140, 50))


        pygame.display.flip()

        #Ya cuando alguien de los dos gane la partida
        if board.is_game_over():
            result = board.result()
            font = pygame.font.SysFont(None, 60)
            if result == "1-0":
                msg = "¡Jaque mate! Ganan Blancas"
            elif result == "0-1":
                msg = "¡Jaque mate! Ganan Negras"
            else:
                msg = "¡Tablas!"

            text = font.render(msg, True, (255, 0, 0))
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, rect)
            pygame.display.flip()
            pygame.time.wait(4000)
            running = False
            continue

        #Revisa todo lo que esta haciendo el jugador
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and board.turn == (chess.WHITE if player_is_white else chess.BLACK):
                # Verificar clic en el botón de rendición
                pos = pygame.mouse.get_pos()
                surrender_btn = pygame.Rect(BOARD_WIDTH + 40, 100, 160, 40)
                if surrender_btn.collidepoint(pos):
                    msg = "Te has rendido. ¡Gana Stockfish!"
                    running = False
                    continue
                square = get_square(pygame.mouse.get_pos())
                # Cliclks dentro del tablero
                if square is not None:  
                    if selected_square is None:
                        # Seleccionar pieza si es del color del jugador
                        piece = board.piece_at(square)
                        # // Se calculan los movimientos legales de esa pieza
                        if piece and piece.color == (chess.WHITE if player_is_white else chess.BLACK):
                            selected_square = square
                            legal_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_square]
                        else:
                            selected_square = None
                            legal_moves = []
                    else:
                        # Intentar mover si ya habia una seleccion previa
                        move = chess.Move(selected_square, square)
                        if move in board.legal_moves:
                            piece = board.piece_at(selected_square)
                            target_piece = board.piece_at(square)
                            piece_symbol = piece.symbol()
                            #Regitrar la captura de ficha
                            if target_piece:
                                if target_piece.color == chess.WHITE:
                                    white_captured.append(target_piece.symbol())
                                else:
                                    black_captured.append(target_piece.symbol())

                            animate_move(screen, board, piece_symbol, selected_square, square)
                            board.push(move)
                            move_log.append(board.peek().uci())
                            move_sound.play()
                            
                            # Reinicia la seleccion del jugaror
                            selected_square = None
                            legal_moves = []

                            # Movimiento de Stockfish
                            result = engine.play(board, chess.engine.Limit(time=stockfish_thinking_time))
                            stockfish_move = result.move
                            captured = board.piece_at(stockfish_move.to_square)
                            if captured:
                                if captured.color == chess.WHITE:
                                    white_captured.append(captured.symbol())
                                else:
                                    black_captured.append(captured.symbol())

                            piece_symbol = board.piece_at(stockfish_move.from_square).symbol()
                            animate_move(screen, board, piece_symbol, stockfish_move.from_square, stockfish_move.to_square)
                            board.push(stockfish_move)
                            move_log.append(board.peek().uci())
                            move_sound.play()
                        else:
                            # Si el segundo clic no es movimiento legal, reiniciar selección
                            selected_square = None
                            legal_moves = []


    clock.tick(60)#Limita los fotogramas
    engine.quit()#Cierra tockfish y libera u proceso en segundo plano
    pygame.quit()#inzaliza y elimina toods lo procesos como imagenes, sonidos
    
#Asegura de su ejecucion solo si se ejecuta directamente desde este archivo y no desde otro script
if __name__ == "__main__":
    main()