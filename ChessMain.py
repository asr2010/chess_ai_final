# main driver file
# handle the inputs
# display the current state
import csv
import random

import pygame as p
import numpy as np

import ChessEngine
import SmartMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8  # 8X8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}


def wallGenerator(mode):
    walls = []
    if mode == 'demo':
        wall1_row = random.randrange(2, 4)
        wall1_col = random.randrange(0, 8)
        wall2_row = random.randrange(4, 6)
        wall2_col = random.randrange(0, 8)
        new_wall = [(wall1_row, wall1_col), (wall2_row, wall2_col)]
        walls.append(new_wall)
    elif mode == 'exp':
        while len(walls) < 100:
            wall1_row = random.randrange(2, 4)
            wall1_col = random.randrange(0, 8)
            wall2_row = random.randrange(4, 6)
            wall2_col = random.randrange(0, 8)
            new_wall = [(wall1_row, wall1_col), (wall2_row, wall2_col)]
            if new_wall in walls:
                continue
            else:
                walls.append(new_wall)
    return walls


# Initialize a global dictionary of images
# called exact once in main

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))


# Main Driver
# Handle User Input
# Display current state

def main(mode, wall, board, filename, score_tree, score_rand):
    p.init()

    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState(wall, board)
    validMoves = gs.getValidMoves()
    moveMade = False

    loadImages()  # only once
    sqSelected = ()  # keep track of the last click of the user (row,col)
    playerClicks = []  # keep track of player clicks

    gameOver = False
    running = True

    playerOne = 0  # Human : 0, Tree AI : 1, Random AI : 2
    playerTwo = 1  # AI

    if mode == 'exp':
        playerOne = random.randint(1, 2);
        playerTwo = 2 if playerOne == 1 else 1

    while running:
        humanTurn = (gs.whiteToMove and playerOne == 0) or (not gs.whiteToMove and playerTwo == 0)
        treeAiTurn = (gs.whiteToMove and playerOne == 1) or (not gs.whiteToMove and playerTwo == 1)
        randAiTurn = (gs.whiteToMove and playerOne == 2) or (not gs.whiteToMove and playerTwo == 2)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # add drag piece functionality
            elif e.type == p.MOUSEBUTTONDOWN:
                moveMade, sqSelected, playerClicks = drag_piece_functionality(gameOver, gs, humanTurn, moveMade,
                                                                              playerClicks, sqSelected, validMoves)
            # key handler
            elif e.type == p.KEYDOWN:
                gameOver, gs, moveMade, playerClicks, sqSelected, validMoves = keystroke_handler(e, gameOver, gs,
                                                                                                 moveMade, playerClicks,
                                                                                                 sqSelected, validMoves,
                                                                                                 wall)

        # Tree AI Move maker
        if not gameOver and treeAiTurn:
            validMoves = gs.getValidMoves()
            AImove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AImove is None:
                AImove = SmartMoveFinder.findRandomMove(validMoves)
            print(AImove.getChessNotation())
            gs.makeMove(AImove)
            moveMade = True

        # Random AI Move maker
        if not gameOver and randAiTurn:
            validMoves = gs.getValidMoves()
            AImove = SmartMoveFinder.findRandomMove(validMoves)
            print(AImove.getChessNotation())
            gs.makeMove(AImove)
            moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            # gs.checkRemainingPieces(gs.board)

        drawGameState(screen, gs, validMoves, sqSelected, wall)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black Wins")

            else:
                drawText(screen, "White Wins")

        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate")
        elif gs.drawGame:
            gameOver = True
            drawText(screen, "Draw by Repetition")

        clock.tick(MAX_FPS)
        p.display.flip()
        if gameOver and mode == 'exp':
            # game_number
            game_log = []
            game_log.append(experiment_count)
            # player 1
            game_log.append('Tree AI' if (playerOne == 1) else 'Random AI')
            # player 2
            game_log.append('Tree AI' if (playerTwo == 1) else 'Random AI')
            # wall 1 position
            game_log.append(wall[0])
            # wall 2 position
            game_log.append(wall[1])
            # result
            if gs.staleMate:
                game_log.append('Stalemate')
                score_tree += 0.5
                score_rand += 0.5
            elif gs.drawGame:
                game_log.append('Draw')
                score_tree += 0.5
                score_rand += 0.5


            elif gs.checkMate:
                winning_color = 'Black' if gs.whiteToMove else 'White'
                winning_player = playerOne if winning_color == 'White' else playerTwo
                winning_player_name = "Tree AI" if winning_player == 1 else "Random AI"
                game_log.append(winning_color + " - " + winning_player_name)
                if winning_player_name == 'Tree AI':
                    score_tree += 1
                elif winning_player_name == 'Random AI':
                    score_rand += 1

            game_log.append(score_tree)
            game_log.append(score_rand)
            export_to_csv(game_log, filename)
            break
    return (score_tree, score_rand)


def keystroke_handler(e, gameOver, gs, moveMade, playerClicks, sqSelected, validMoves, wall):
    if e.key == p.K_z:  # undo when 'z' is pressed
        gs.undoMove()
        moveMade = True
        gameOver = False
    if e.key == p.K_r:  # reset the game
        gs = ChessEngine.GameState(wall)
        validMoves = gs.getValidMoves()
        sqSelected = ()
        playerClicks = []
        moveMade = False
        gameOver = False
    return gameOver, gs, moveMade, playerClicks, sqSelected, validMoves


def drag_piece_functionality(gameOver, gs, humanTurn, moveMade, playerClicks, sqSelected, validMoves):
    if not gameOver and humanTurn:
        location = p.mouse.get_pos()  # (x,y) coordinates for the mouse
        col = location[0] // SQ_SIZE
        row = location[1] // SQ_SIZE
        if sqSelected == (row, col):
            sqSelected = ()  # undo select
            playerClicks = []  # clear player clicks
        else:
            sqSelected = (row, col)
            playerClicks.append(sqSelected)
        if len(playerClicks) == 2:  # 2 clicks recorded, make the move
            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
            print(move.getChessNotation())
            if move in validMoves:
                gs.makeMove(move)
                moveMade = True
                sqSelected = ()
                playerClicks = []
            else:
                playerClicks = [sqSelected]
    return moveMade, sqSelected, playerClicks


# Highlight saquare and moves

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # moves
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


# Responsible for graphics within a current game state

def drawGameState(screen, gs, validMoves, sqSelected, wall):
    drawBoard(screen)  # draw squares
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board, wall)  # draw pieces


def drawBoard(screen):
    colors = [p.Color('white'), p.Color('gray')]
    # top left square is always white
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# draw pieces from GameState.board
def drawPieces(screen, board, wall):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            # Check if not empty
            if (r, c) == wall[0] or (r, c) == wall[1]:
                p.draw.rect(screen, 'red', p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if piece != '--' and piece != '00':
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawText(screen, text):
    font = p.font.SysFont("Helvitica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


def export_to_csv(game_log, filename):
    headers = ['Game Number', 'Player 1', 'Player 2', 'Wall 1', 'Wall 2', 'Winner', 'Score Tree', 'Score Random']
    file = open(filename, 'a', newline='')
    with file:
        write = csv.writer(file)
        if experiment_count == 1:
            write.writerow(headers)
        write.writerow(game_log)
    file.close()


if __name__ == '__main__':
    mode = 'exp'
    experiment_count = 1

    walls = wallGenerator(mode)
    board_1 = np.array([
        [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ],
        [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ],
        [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['--', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ],
        [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['--', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', '--', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ],
        [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', '--', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
    ])
    if mode == 'exp':
        gs_counter = 0
        for boards in board_1:
            gs_counter += 1
            experiment_count = 1

            score_treeai = 0
            score_randai = 0
            filename = 'score_gamestate_' + str(gs_counter) + '.csv'
            file = open(filename, 'w', newline='')
            file.close()
            for i in range(100):
                board = boards.copy()
                score = main(mode, walls[i], board, filename, score_treeai, score_randai)
                score_treeai = score[0]
                score_randai = score[1]
                experiment_count += 1

    else:
        main(mode, walls[0])
