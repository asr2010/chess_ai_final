import random
import torch as tr
import numpy as np
import ChessMain
import numpy as np


pieceScore = {"K": 1, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 2}
pieces = ["bK","bQ","bR","bB","bN","bp","wK","wQ","wR","wB","wN","wp","--"]
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
states = []
win = 0
piece = []
hotencode = []

hotencode_1 = []
final=[]
nb_classes = 13

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves):
    states.append([gs.board])
    print(states)
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    if (gs.checkMate == True or gs.staleMate == True or gs.drawGame == True):
        checkRemPieces(gs,gs.board)
        print(len(states))
        indices_to_one_hot(states)
    return nextMove

def checkRemPieces(gs,board):
    if gs.checkMate == True and gs.whiteToMove == True:
        count = (np.count_nonzero(board=='wp') + np.count_nonzero(board=='wR') + np.count_nonzero(board=='wB') + np.count_nonzero(board=='wK') + np.count_nonzero(board=='wQ') + np.count_nonzero(board=='wN') + np.count_nonzero(board=='wK'))-1
    elif gs.checkMate == True and gs.whiteToMove == False:
        count = -1*((np.count_nonzero(board=='bp') + np.count_nonzero(board=='bR') + np.count_nonzero(board=='bB') + np.count_nonzero(board=='bK') + np.count_nonzero(board=='bQ') + np.count_nonzero(board=='bN') + np.count_nonzero(board=='bK'))-1)
    else:
        count = 0
    print(count)
    return count


# def encode(gs):
#     symbols = tr.tensor([1,9,5,3,3,2,-1,-9,-5,-3,-3,-2,0]).reshape(-1,1,1)
#     onehot = (symbols == gs.board).float()
#     print(onehot)
#     return onehot

    # for i in states:
    #     for j in i:
    #         for k in j:
    #             for l in k:
    #                 piece.append(pieces.index(l))
    #     for k in range(8):
    #         hotencode = [[1 if piece[i] else 0 for _ in range(13)] for i in range(8)]
    #         print(hotencode)
    #         hotencode_list.append(hotencode)
    #     final.append(hotencode_list)
    # print(final)
    
    
    #         hotencode_list.append(hotencode)
    #         print("---------------------------------\n")
    #     print(hotencode_list)
    # print(len(hotencode_list))


def indices_to_one_hot(states):
    # Convert an iterable of indices to one-hot encoded labels.
    for i in states:
        for j in range(len(pieces)):
            for k in i:
                for l in k:
                    for m in l:
                        if m == pieces[j]:
                            hotencode.append(1)
                        else:
                            hotencode.append(0)
    #targets = np.array(hotencode).reshape(-1)
    #array_he = np.eye(nb_classes)[targets]
    #hotencode = [[i for i in j] for j in array_he]
    hotencode_list = np.array(hotencode)
    hot_arr = hotencode_list.reshape(len(states),832)
    print(hot_arr[0])
    print(len(hot_arr))
    # array_he.reshape(64,-1)
    # print(array_he[:65])
    # for i in array_he:
    #     hotencode = []
    #     for j in range(64):
    #         hotencode.append(i)
    #     hotencode_1 = np.array(hotencode).reshape(-1)
    #     hotencode_list.append(hotencode_1)
    # print(len(hotencode_list))
    # return np.eye(nb_classes)[targets]

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        # print(move.pieceMoved)
        # print((move.startRow, move.startCol))
        # print((move.endRow, move.endCol))
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE

    score = 0

    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score
