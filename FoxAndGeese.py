import random
import sys
import time
import copy
# interfata grafica
import pygame
import pygame.gfxdraw
from pygame.locals import *

MAX = sys.maxsize
MIN = -MAX
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
ORANGE = (255,165,0)


def matrixToString(m):  # converte matrice m in string pt printare
    s = ""
    for line in m:
        for elem in line:
            s = s + str(elem)
        s = s + '\n'

    return s


def fHash(m, depth):  # functie de hashare a matr m la adancime depth
    s = ""
    for line in m:
        for elem in line:
            s = s + str(elem)
    s = s + str(depth)
    x = hash(s)
    return x


class Move:
    def __init__(self, score, depth=-1, linInit=-1, colInit=-1, linFin=-1, colFin=-1):
        self.score = score
        self.depth = depth
        self.linInit = linInit
        self.colInit = colInit
        self.linFin = linFin
        self.colFin = colFin


class Game:
    def __init__(self):

        # mod de joc
        self.gameMode = 0
        # ai gasca sau vulpe
        self.gasca = False
        # dificultate = adancime max graf
        self.maxDepth = 0
        # alfabeta/ minmax
        self.isAlphaBeta = False

        self.pozMap = {}  # map de poziitii deja calculate
        # nr noduri calculate la extinderea grafului
        self.nrNod = 0
        # nr de noduri calculate la mai multe mutari
        self.nodSet = []
        # nr max noduri generate la o mutare
        self.nrMaxNod = 0
        # nr max noduri generate la o mutare
        self.nrMinNod = MAX


        self.board = []  # initializam board-ul de joc
        for i in range(13):
            line = []
            if i < 4 or i > 8:
                if i % 2 == 0:
                    for j in range(13):
                        if j < 4 or j > 8:
                            line.append("X")
                        elif j % 2 == 0:
                            line.append("·")
                        else:
                            line.append("-")
                else:
                    for j in range(13):
                        if j < 4 or j > 8:
                            line.append("X")
                        elif j % 2 == 0:
                            line.append("|")
                        else:
                            if int(i / 2) % 2 == 1:
                                if int(j / 2) % 2 == 0:
                                    line.append("/")
                                else:
                                    line.append("\\")
                            else:
                                if int(j / 2) % 2 == 0:
                                    line.append("\\")
                                else:
                                    line.append("/")
            else:
                for j in range(13):
                    if i % 2 == 0:
                        if j % 2 == 0:
                            line.append("·")
                        else:
                            line.append("-")
                    else:
                        if j % 2 == 0:
                            line.append("|")
                        else:
                            if int(i / 2) % 2 == 0:
                                if int(j / 2) % 2 == 0:
                                    line.append("\\")
                                else:
                                    line.append("/")
                            else:
                                if int(j / 2) % 2 == 0:
                                    line.append("/")
                                else:
                                    line.append("\\")

            self.board.append(line)

        # plasam vulpea si gastile
        self.board[4][6] = "V"
        self.pozVulpe = (4, 6)
        for i in range(4, 13, 2):
            if i < 8:
                self.board[i][0] = self.board[i][12] = "G"
            else:
                for j in range(0, 13, 2):
                    if self.board[i][j] == "·":
                        self.board[i][j] = "G"
        self.nrGaste = 17

    def __str__(self):
        return matrixToString(self.board)

    def isEndGame(self):
        # castiga vulpea
        if self.nrGaste < 4:
            return True
        # castiga gastele
        i = self.pozVulpe[0]
        j = self.pozVulpe[1]
        moves = self.checkMove(i, j)
        captures = self.checkCapture(i, j)
        if len(moves) == 0 and len(captures) == 0:
            return True
        # jocul continua
        return False

    # functie evaluare stare curenta 1
    def evaluate(self):
        if self.isEndGame():
            if self.nrGaste < 4:
                return MIN
            else:
                return MAX
        else:
            i = self.pozVulpe[0]
            j = self.pozVulpe[1]
            nav = self.checkMove(i, j)
            capt = self.checkCapture(i, j)
            for item in nav:
                temp = self.checkMove(item[0], item[1])
                for poz in temp:
                    if poz not in nav:
                        nav.append(poz)
            score = self.nrGaste * 100 - len(nav) - len(capt)
            # print(score)
            return score

    # functie evaluare stare curenta 2
    def evaluate2(self):
        if self.isEndGame():
            if self.nrGaste < 4:
                return MIN
            else:
                return MAX
        else:
            i = self.pozVulpe[0]
            j = self.pozVulpe[1]
            nav = self.checkMove(i, j)
            capt = self.checkCapture(i, j)
            score = self.nrGaste * 100 - len(nav) - len(capt)
            return score

    # verifica unde se poate muta o piesa
    def checkMove(self, i, j):
        moves = []
        # stanga sus
        if i >= 2 and j >= 2:
            if self.board[i - 1][j - 1] == "\\":
                if self.board[i - 2][j - 2] == "·":
                    moves.append((i - 2, j - 2))
        # dreapta sus
        if i >= 2 and j <= 10:
            if self.board[i - 1][j + 1] == "/":
                if self.board[i - 2][j + 2] == "·":
                    moves.append((i - 2, j + 2))
        # stanga jos
        if i <= 10 and j >= 2:
            if self.board[i + 1][j - 1] == "/":
                if self.board[i + 2][j - 2] == "·":
                    moves.append((i + 2, j - 2))
        # dreapta jos
        if i <= 10 and j < 10:
            if self.board[i + 1][j + 1] == "\\":
                if self.board[i + 2][j + 2] == "·":
                    moves.append((i + 2, j + 2))
        # deasupra
        if i >= 2:
            if self.board[i - 2][j] == "·":
                moves.append((i - 2, j))

        # sub
        if i <= 10:
            if self.board[i + 2][j] == "·":
                moves.append((i + 2, j))
        # stanga
        if j >= 2:
            if self.board[i][j - 2] == "·":
                moves.append((i, j - 2))
        # dreapta
        if j <= 10:
            if self.board[i][j + 2] == "·":
                moves.append((i, j + 2))

        return moves

    # verifica unde poate sari o piesa, folosit la sariturile vulpii
    def checkCapture(self, i, j):
        moves = []
        # stanga sus
        if i >= 4 and j >= 4:
            if self.board[i - 1][j - 1] == "\\":
                if self.board[i - 2][j - 2] == "G":
                    if self.board[i - 4][j - 4] == "·":
                        moves.append((i - 4, j - 4))
        # dreapta sus
        if i >= 4 and j <= 8:
            if self.board[i - 1][j + 1] == "/":
                if self.board[i - 2][j + 2] == "G":
                    if self.board[i - 4][j + 4] == "·":
                        moves.append((i - 4, j + 4))
        # stanga jos
        if i <= 8 and j >= 4:
            if self.board[i + 1][j - 1] == "/":
                if self.board[i + 2][j - 2] == "G":
                    if self.board[i + 4][j - 4] == "·":
                        moves.append((i + 4, j - 4))
        # dreapta jos
        if i <= 8 and j <= 8:
            if self.board[i + 1][j + 1] == "\\":
                if self.board[i + 2][j + 2] == "G":
                    if self.board[i + 4][j + 4] == "·":
                        moves.append((i + 4, j + 4))
        # deasupra
        if i >= 4:
            if self.board[i - 2][j] == "G":
                if self.board[i - 4][j] == "·":
                    moves.append((i - 4, j))
        # sub
        if i <= 8:
            if self.board[i + 2][j] == "G":
                if self.board[i + 4][j] == "·":
                    moves.append((i + 4, j))
        # stanga
        if j >= 4:
            if self.board[i][j - 2] == "G":
                if self.board[i][j - 4] == "·":
                    moves.append((i, j - 4))
        # dreapta
        if j <= 8:
            if self.board[i][j + 2] == "G":
                if self.board[i][j + 4] == "·":
                    moves.append((i, j + 4))

        return moves

    # fc alg minmax
    def minMax(self, depth, isJmax, captured=False):

        # crestem nr noduri generate la mutarea curenta
        self.nrNod += 1
        # daca este deja hashat, returnam direct
        hsh = fHash(self.board, depth)
        if hsh in self.pozMap:
            return self.pozMap[hsh]

        score = self.evaluate()
        # print(score)

        if self.isEndGame() or depth == self.maxDepth - 1:  # final de joc sau adancime max
            return score

        # simulam mutari si apelam minmax recursiv
        if isJmax:  # gaste
            score = MIN
            for lineIdx, line in enumerate(self.board):
                for colIdx, elem in enumerate(line):
                    if elem == "G":
                        self.board[lineIdx][colIdx] = "·"
                        moves = self.checkMove(lineIdx, colIdx)
                        for move in moves:
                            self.board[move[0]][move[1]] = "G"
                            val = self.minMax(depth + 1, not isJmax)
                            score = max(score, val)
                            self.board[move[0]][move[1]] = "·"
                        self.board[lineIdx][colIdx] = "G"
            self.pozMap[hsh] = score
            return score
        else:  # vulpe
            score = MAX
            lineIdx = self.pozVulpe[0]
            colIdx = self.pozVulpe[1]
            self.board[lineIdx][colIdx] = "·"

            if not captured:
                moves = self.checkMove(lineIdx, colIdx)
                for move in moves:  # miscari
                    self.board[move[0]][move[1]] = "V"
                    self.pozVulpe = (move[0], move[1])
                    val = self.minMax(depth + 1, not isJmax)
                    score = min(val, score)
                    self.board[move[0]][move[1]] = "·"
                    self.pozVulpe = (lineIdx, colIdx)

            captures = self.checkCapture(lineIdx, colIdx)
            for capture in captures:  # capturi gaste
                self.board[capture[0]][capture[1]] = "V"
                self.pozVulpe = (capture[0], capture[1])
                self.board[int(abs(capture[0] + lineIdx)/2)][int(abs(capture[1] + colIdx)/2)] = "·"
                self.nrGaste -= 1

                val = self.minMax(depth + 1, isJmax, True)
                score = min(val, score)

                self.nrGaste += 1
                self.board[capture[0]][capture[1]] = "·"
                self.pozVulpe = (lineIdx, colIdx)
                self.board[int(abs(capture[0] + lineIdx)/2)][int(abs(capture[1] + colIdx)/2)] = "G"

            if captured and len(captures) == 0:
                self.board[lineIdx][colIdx] = "V"
                score = self.minMax(depth + 1, not isJmax)

            self.board[lineIdx][colIdx] = "V"

            self.pozMap[hsh] = score
            return score

    # fc alg alfabeta
    def alphaBeta(self, depth, isJmax, alpha, beta, captured=False):
        # crestem nr noduri generate la mutarea curenta
        self.nrNod += 1
        # daca este deja hashat, returnam direct
        hsh = fHash(self.board, depth)
        if hsh in self.pozMap:
            return self.pozMap[hsh]

        score = self.evaluate()

        if self.isEndGame() or depth == self.maxDepth - 1:  # final de joc sau adancime max
            return score

        if isJmax:  # gaste
            score = MIN
            for lineIdx, line in enumerate(self.board):
                for colIdx, elem in enumerate(line):
                    if elem == "G":
                        self.board[lineIdx][colIdx] = "·"
                        moves = self.checkMove(lineIdx, colIdx)
                        for move in moves:
                            self.board[move[0]][move[1]] = "G"
                            val = self.alphaBeta(depth + 1, not isJmax, alpha, beta)
                            score = max(score, val)
                            self.board[move[0]][move[1]] = "·"
                            alpha = max(alpha, score)
                            # daca se atinge conditia de oprire
                            if beta <= alpha:
                                self.board[lineIdx][colIdx] = "G"
                                self.pozMap[hsh] = score
                                return score

                        self.board[lineIdx][colIdx] = "G"
            self.pozMap[hsh] = score
            return score
        else:  # vulpe
            score = MAX
            lineIdx = self.pozVulpe[0]
            colIdx = self.pozVulpe[1]
            self.board[lineIdx][colIdx] = "·"

            if not captured:
                moves = self.checkMove(lineIdx, colIdx)
                for move in moves:  # miscari
                    self.board[move[0]][move[1]] = "V"
                    self.pozVulpe = (move[0], move[1])
                    val = self.alphaBeta(depth + 1, not isJmax, alpha, beta)
                    score = min(val, score)
                    self.board[move[0]][move[1]] = "·"
                    self.pozVulpe = (lineIdx, colIdx)
                    beta = min(beta, score)
                    # daca se atinge conditia de oprire
                    if beta <= alpha:
                        self.board[lineIdx][colIdx] = "V"
                        self.pozMap[hsh] = score
                        return score


            captures = self.checkCapture(lineIdx, colIdx)
            for capture in captures:  # capturi gaste
                self.board[capture[0]][capture[1]] = "V"
                self.pozVulpe = (capture[0], capture[1])
                self.board[int(abs(capture[0] + lineIdx) / 2)][int(abs(capture[1] + colIdx) / 2)] = "·"
                self.nrGaste -= 1

                val = self.alphaBeta(depth + 1, isJmax, alpha, beta, True)
                score = min(val, score)

                self.nrGaste += 1
                self.board[capture[0]][capture[1]] = "·"
                self.pozVulpe = (lineIdx, colIdx)
                self.board[int(abs(capture[0] + lineIdx) / 2)][int(abs(capture[1] + colIdx) / 2)] = "G"
                # daca se atinge conditia de oprire
                if beta <= alpha:
                    self.board[lineIdx][colIdx] = "V"
                    self.pozMap[hsh] = score
                    return score

            if captured and len(captures) == 0:
                self.board[lineIdx][colIdx] = "V"
                score = self.alphaBeta(depth + 1, not isJmax, alpha, beta)

            self.board[lineIdx][colIdx] = "V"

            self.pozMap[hsh] = score
            return score

    # cauta mutare gaste dupa scor
    def findGmove(self, score):
        movelist = []
        for lineIdx, line in enumerate(self.board):
            for colIdx, elem in enumerate(line):
                if elem == "G":
                    self.board[lineIdx][colIdx] = "·"
                    moves = self.checkMove(lineIdx, colIdx)
                    for move in moves:
                        self.board[move[0]][move[1]] = "G"
                        if self.isAlphaBeta:
                            val = self.alphaBeta(1, False, MIN, MAX)
                        else:
                            val = self.minMax(1, False)
                        if val == score:
                            movelist.append((lineIdx, colIdx, move[0], move[1]))

                        self.board[move[0]][move[1]] = "·"
                    self.board[lineIdx][colIdx] = "G"

        return movelist[random.randint(0, len(movelist) - 1)]

    # cauta mutare/salt pt vulpe dupa scor
    def findVmove(self, score, captured):
        lineIdx = self.pozVulpe[0]
        colIdx = self.pozVulpe[1]
        self.board[lineIdx][colIdx] = "·"

        # daca nu a fost capturata o gasca anterior
        if not captured:
            moves = self.checkMove(lineIdx, colIdx)
            for move in moves:  # miscari
                self.board[move[0]][move[1]] = "V"
                self.pozVulpe = (move[0], move[1])
                if self.isAlphaBeta:
                    val = self.alphaBeta(1, True, MIN, MAX)
                else:
                    val = self.minMax(1, True)
                if val == score:
                    self.board[move[0]][move[1]] = "·"
                    self.pozVulpe = (lineIdx, colIdx)
                    self.board[lineIdx][colIdx] = "V"
                    return (lineIdx,  colIdx, move[0], move[1])
                self.board[move[0]][move[1]] = "·"
                self.pozVulpe = (lineIdx, colIdx)

        captures = self.checkCapture(lineIdx, colIdx)
        for capture in captures:  # capturi gaste
            self.board[capture[0]][capture[1]] = "V"
            self.pozVulpe = (capture[0], capture[1])
            self.board[int(abs(capture[0] + lineIdx) / 2)][int(abs(capture[1] + colIdx) / 2)] = "·"
            self.nrGaste -= 1
            if self.isAlphaBeta:
                val = self.alphaBeta(1, False, MIN, MAX, True)
            else:
                val = self.minMax(1, False, True)
            if val == score:
                self.nrGaste += 1
                self.board[capture[0]][capture[1]] = "·"
                self.pozVulpe = (lineIdx, colIdx)
                self.board[int(abs(capture[0] + lineIdx) / 2)][int(abs(capture[1] + colIdx) / 2)] = "G"
                self.board[lineIdx][colIdx] = "V"
                return (lineIdx,  colIdx, capture[0], capture[1])

            self.nrGaste += 1
            self.board[capture[0]][capture[1]] = "·"
            self.pozVulpe = (lineIdx, colIdx)
            self.board[int(abs(capture[0] + lineIdx) / 2)][int(abs(capture[1] + colIdx) / 2)] = "G"

        # nu mai are unde sa sara
        self.board[lineIdx][colIdx] = "V"
        return (lineIdx, colIdx, lineIdx, colIdx)

    def playGUI(self):
        # deschidem GUI
        modifier = 50
        pygame.init()

        # initializam fereastra
        mwidth = 13 * modifier
        mheight = 13 * modifier
        winwidth = mwidth + 2 * modifier
        # poz curenta in log de afisare
        crtPoz = 0
        # poz maxima in log
        maxPoz = 26

        screen = pygame.display.set_mode((winwidth, mheight))
        pygame.display.set_caption('Dumitriu_Razvan_Andrei_VulpiSiGaste')

        # alegem modul de joc
        midx = winwidth // 2
        midy = mheight // 2
        # creem si afisam butoanele
        midRefLeft = midx - modifier * 2
        midRefTop = midy - modifier
        rect = Rect(midRefLeft, midRefTop, 4 * modifier, 2 * modifier)
        pygame.draw.rect(screen, WHITE, rect)

        rect = Rect(midRefLeft, midRefTop - 4 * modifier, 4 * modifier, 2 * modifier)
        pygame.draw.rect(screen, WHITE, rect)

        rect = Rect(midRefLeft, midRefTop + 4 * modifier, 4 * modifier, 2 * modifier)
        pygame.draw.rect(screen, WHITE, rect)

        font = pygame.font.SysFont('arial', 30)
        text = font.render("Alegeti modul de joc:", True, WHITE)
        textRect = text.get_rect()
        textRect.center = (midx, midy - 6 * modifier)
        screen.blit(text, textRect)

        text = font.render("Player vs AI", True, BLACK)
        textRect = text.get_rect()
        textRect.center = (midx, midy - 4 * modifier)
        screen.blit(text, textRect)

        text = font.render("Player vs Player", True, BLACK)
        textRect = text.get_rect()
        textRect.center = (midx, midy)
        screen.blit(text, textRect)

        text = font.render("AI vs AI", True, BLACK)
        textRect = text.get_rect()
        textRect.center = (midx, midy + 4 * modifier)
        screen.blit(text, textRect)

        pygame.display.update()
        # asteptam input
        ok = True
        while ok:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    poz = pygame.mouse.get_pos()
                    x = poz[0]
                    y = poz[1]
                    if midx - 2 * modifier <= x <= midx + 2 * modifier:
                        if midy - 5 * modifier <= y <= midy - 3 * modifier:
                            self.gameMode = 1
                            ok = False
                        if midy - modifier <= y <= midy + modifier:
                            self.gameMode = 2
                            ok = False
                        # if midy + 3 * modifier <= y <= midy + 5 * modifier:
                            # self.gameMode = 3
                            # ok = False
                    break
        if self.gameMode == 1:
            # se alege simbolul de joc
            # creem si afisam butoanele
            screen.fill(BLACK)
            rect = Rect(midRefLeft, midRefTop - 2 * modifier, 4 * modifier, 2 * modifier)
            pygame.draw.rect(screen, WHITE, rect)

            rect = Rect(midRefLeft, midRefTop + 2 * modifier, 4 * modifier, 2 * modifier)
            pygame.draw.rect(screen, WHITE, rect)

            text = font.render("Alegeti simbolul de joc:", True, WHITE)
            textRect = text.get_rect()
            textRect.center = (midx, midy - 6 * modifier)
            screen.blit(text, textRect)

            text = font.render("Vulpi", True, BLACK)
            textRect = text.get_rect()
            textRect.center = (midx, midy - 2 * modifier)
            screen.blit(text, textRect)

            text = font.render("Gaste", True, BLACK)
            textRect = text.get_rect()
            textRect.center = (midx, midy + 2 * modifier)
            screen.blit(text, textRect)

            pygame.display.update()
            # asteptam input
            ok = True
            while ok:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        poz = pygame.mouse.get_pos()
                        x = poz[0]
                        y = poz[1]
                        if midx - 2 * modifier <= x <= midx + 2 * modifier:
                            if midy - 3 * modifier <= y <= midy - modifier:
                                self.gasca = True
                                ok = False
                            if midy + modifier <= y <= midy + 3 * modifier:
                                self.gasca = False
                                ok = False
                        break

            # se alege dificultatea
            # creem si afisam butoanele
            screen.fill(BLACK)
            rect = Rect(midRefLeft, midRefTop, 4 * modifier, 2 * modifier)
            pygame.draw.rect(screen, WHITE, rect)

            rect = Rect(midRefLeft, midRefTop - 4 * modifier, 4 * modifier, 2 * modifier)
            pygame.draw.rect(screen, WHITE, rect)

            rect = Rect(midRefLeft, midRefTop + 4 * modifier, 4 * modifier, 2 * modifier)
            pygame.draw.rect(screen, WHITE, rect)

            font = pygame.font.SysFont('arial', 30)
            text = font.render("Alegeti dificultatea:", True, WHITE)
            textRect = text.get_rect()
            textRect.center = (midx, midy - 6 * modifier)
            screen.blit(text, textRect)

            text = font.render("Incepator", True, BLACK)
            textRect = text.get_rect()
            textRect.center = (midx, midy - 4 * modifier)
            screen.blit(text, textRect)

            text = font.render("Mediu", True, BLACK)
            textRect = text.get_rect()
            textRect.center = (midx, midy)
            screen.blit(text, textRect)

            text = font.render("Avansat", True, BLACK)
            textRect = text.get_rect()
            textRect.center = (midx, midy + 4 * modifier)
            screen.blit(text, textRect)

            pygame.display.update()
            # asteptam input
            ok = True
            while ok:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        poz = pygame.mouse.get_pos()
                        x = poz[0]
                        y = poz[1]
                        if midx - 2 * modifier <= x <= midx + 2 * modifier:
                            if midy - 5 * modifier <= y <= midy - 3 * modifier:
                                self.maxDepth = 2
                                ok = False
                            if midy - modifier <= y <= midy + modifier:
                                self.maxDepth = 3
                                ok = False
                            if midy + 3 * modifier <= y <= midy + 5 * modifier:
                                self.maxDepth = 5
                                ok = False
                        break

            # se alege algoritmul de joc
            # creem si afisam butoanele
            screen.fill(BLACK)
            rect = Rect(midRefLeft, midRefTop - 2 * modifier, 4 * modifier, 2 * modifier)
            pygame.draw.rect(screen, WHITE, rect)

            rect = Rect(midRefLeft, midRefTop + 2 * modifier, 4 * modifier, 2 * modifier)
            pygame.draw.rect(screen, WHITE, rect)

            text = font.render("Alegeti algoritmul de joc:", True, WHITE)
            textRect = text.get_rect()
            textRect.center = (midx, midy - 6 * modifier)
            screen.blit(text, textRect)

            text = font.render("MinMax", True, BLACK)
            textRect = text.get_rect()
            textRect.center = (midx, midy - 2 * modifier)
            screen.blit(text, textRect)

            text = font.render("AlphaBeta", True, BLACK)
            textRect = text.get_rect()
            textRect.center = (midx, midy + 2 * modifier)
            screen.blit(text, textRect)

            pygame.display.update()
            # asteptam input
            ok = True
            while ok:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        poz = pygame.mouse.get_pos()
                        x = poz[0]
                        y = poz[1]
                        if midx - 2 * modifier <= x <= midx + 2 * modifier:
                            if midy - 3 * modifier <= y <= midy - modifier:
                                self.isAlphaBeta = False
                                ok = False
                            if midy + modifier <= y <= midy + 3 * modifier:
                                self.isAlphaBeta = True
                                ok = False
                        break
            screen.fill(BLACK)


            # timp de inceput de joc
            startTime = time.time()
            # timp minim mutare AI
            minTime = 100
            # timp max mutare AI
            maxTime = 0
            # vector de timpi de mutari
            timeSet = []
            if self.gasca:  # gastele muta primele
                player = True
            else:
                player = False
            # nr mutari
            computerMoves = 0
            playerMoves = 0
            capture = False

            # afisam piesele pe GUI
            for i in range(13):
                for j in range(13):
                    rect = Rect(j * modifier, i * modifier, modifier, modifier)
                    if self.board[i][j] == "X":
                        pygame.draw.rect(screen, BLACK, rect)
                    elif self.board[i][j] == "V":
                        pygame.draw.rect(screen, RED, rect)
                    elif self.board[i][j] == "G":
                        pygame.draw.rect(screen, BLUE, rect)
                    elif self.board[i][j] == "·":
                        pygame.draw.rect(screen, GREEN, rect)
                    else:
                        pygame.draw.rect(screen, WHITE, rect)
                        poz = convertToGUI(i, j, modifier)
                        showSymbol(poz[0], poz[1], screen, self.board[i][j], modifier)
            # initializam fontul
            font = pygame.font.SysFont('arial', 20)
            pygame.display.update()

            while not self.isEndGame():
                if player:  # daca este randul computerului
                    pygame.event.pump()

                    moveTime = time.time()
                    if self.gasca:  # gasca
                        msg = "Gastele muta!"
                        crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, GREEN)
                        computerMoves += 1
                        self.nrNod = 0
                        if self.isAlphaBeta:
                            score = self.alphaBeta(0, self.gasca, MIN, MAX)
                        else:
                            score = self.minMax(0, self.gasca)
                        print(f"{self.nrNod} noduri generate")
                        self.nodSet.append(self.nrNod)
                        if self.nrNod > self.nrMaxNod:
                            self.nrMaxNod = self.nrNod
                        if self.nrNod < self.nrMinNod:
                            self.nrMinNod = self.nrNod
                        print(f"Scor: {score}")
                        move = self.findGmove(score)
                        tGandire = time.time() - moveTime
                        print(f"Timp gandire AI:{tGandire}")
                        timeSet.append(tGandire)
                        if tGandire < minTime:
                            minTime = tGandire
                        if tGandire > maxTime:
                            maxTime = tGandire

                        # afiseaza mutarea
                        msg = f"LinInit:{move[0]}, ColInit:{move[1]}"
                        crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                        msg = f"LinFin:{move[2]}, ColFin:{move[3]}"
                        crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)

                        # actualizeaza placa de joc
                        self.board[move[0]][move[1]] = "·"
                        self.board[move[2]][move[3]] = "G"

                        poz = convertToGUI(move[0], move[1], modifier)
                        rect = Rect(poz[0], poz[1], modifier, modifier)
                        pygame.draw.rect(screen, GREEN, rect)

                        poz = convertToGUI(move[2], move[3], modifier)
                        rect = Rect(poz[0], poz[1], modifier, modifier)
                        pygame.draw.rect(screen, BLUE, rect)

                        msg = f"Gaste ramase:{self.nrGaste}"
                        crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)

                        pygame.display.update()
                        print(self)

                        player = not player
                    else:  # vulpe
                        msg = "Vulpile muta!"
                        crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, GREEN)
                        self.nrNod = 0
                        if self.isAlphaBeta:
                            score = self.alphaBeta(0, self.gasca, MIN, MAX, capture)
                        else:
                            score = self.minMax(0, self.gasca, capture)
                        print(f"{self.nrNod} noduri generate")
                        self.nodSet.append(self.nrNod)
                        if self.nrNod > self.nrMaxNod:
                            self.nrMaxNod = self.nrNod
                        if self.nrNod < self.nrMinNod:
                            self.nrMinNod = self.nrNod
                        print(f"Scor: {score}")
                        move = self.findVmove(score, capture)
                        if move[0] == move[2] and move[1] == move[3]:
                            capture = False
                            player = not player
                        else:
                            tGandire = time.time() - moveTime
                            print(f"Timp gandire AI:{tGandire}")
                            timeSet.append(tGandire)
                            if tGandire < minTime:
                                minTime = tGandire
                            if tGandire > maxTime:
                                maxTime = tGandire
                            msg = f"LinInit:{move[0]}, ColInit:{move[1]}"
                            crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                            msg = f"LinFin:{move[2]}, ColFin:{move[3]}"
                            crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)

                            # mutam vulpea
                            self.board[move[0]][move[1]] = "·"
                            self.board[move[2]][move[3]] = "V"
                            self.pozVulpe = (move[2], move[3])

                            poz = convertToGUI(move[0], move[1], modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, GREEN, rect)

                            poz = convertToGUI(move[2], move[3], modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, RED, rect)

                            # verif daca s a capturat
                            if abs(move[0] - move[2]) == 4 or abs(move[1] - move[3]) == 4:
                                capture = True
                                self.board[int(abs(move[0] + move[2]) / 2)][int(abs(move[1] + move[3]) / 2)] = "·"
                                self.nrGaste -= 1

                                poz = convertToGUI(int(abs(move[0] + move[2]) / 2), int(abs(move[1] + move[3]) / 2), modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, GREEN, rect)
                            else:
                                computerMoves += 1
                                player = not player

                            msg = f"Gaste ramase:{self.nrGaste}"
                            crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                            pygame.display.update()
                            print(self)
                else:  # daca este randul jucatorului

                    pygame.display.update()
                    if self.gasca:  # vulpe
                        linInit = self.pozVulpe[0]
                        colInit = self.pozVulpe[1]
                        msg = "Vulpea muta!"
                        crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, GREEN)
                        moveTime = time.time()
                        ls = self.checkCapture(linInit, colInit)
                        if not capture or len(ls) != 0:  # daca poate muta
                            # get user input
                            while True:
                                ok = True
                                for event in pygame.event.get():
                                    if event.type == QUIT:
                                        pygame.quit()
                                        print(f"Timp minim: {minTime}")
                                        print(f"Timp maxim: {maxTime}")
                                        print(f"Media timpilor:{sum(timeSet) / len(timeSet)}")
                                        timeSet.sort()
                                        print(f"Mediana timpilor: {timeSet[int(len(timeSet) / 2)]}")

                                        print(f"Min noduri generate: {self.nrMinNod}")
                                        print(f"Max noduri generate: {self.nrMaxNod}")
                                        print(f"Media nr de noduri generate: {sum(self.nodSet) / len(self.nodSet)}")
                                        self.nodSet.sort()
                                        print(f"Mediana nr de noduri generate: {self.nodSet[int(len(self.nodSet) / 2)]}")

                                        print(f"Timp de joc:{time.time() - startTime}")

                                        print(f"Nr mutari jucator:{playerMoves} ")
                                        print(f"Nr mutari PC:{computerMoves}")
                                        sys.exit()
                                    if event.type == MOUSEBUTTONDOWN:
                                        poz = pygame.mouse.get_pos()
                                        poz = convertFromGUI(poz[0], poz[1], modifier)
                                        if poz[1] < 13:
                                            ok = False
                                            linFin = poz[0]
                                            colFin = poz[1]
                                            break
                                if not ok:
                                    break
                        tGandire = time.time() - moveTime
                        print(f"Timp gandire jucator:{tGandire}")

                        if capture:  # dupa 1 salt
                            if len(ls) == 0:  # nu mai are unde sa sara
                                capture = False
                                player = not player
                                playerMoves += 1
                            elif (linFin, colFin) in ls:  # continua sa sara
                                self.board[linInit][colInit] = "·"
                                self.board[linFin][colFin] = "V"

                                poz = convertToGUI(linInit, colInit, modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, GREEN, rect)

                                poz = convertToGUI(linFin, colFin, modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, RED, rect)

                                self.pozVulpe = (linFin, colFin)
                                self.nrGaste -= 1

                                self.board[int(abs(linInit + linFin) / 2)][int(abs(colInit + colFin) / 2)] = "·"

                                poz = convertToGUI(int(abs(linInit + linFin) / 2), int(abs(colInit + colFin) / 2), modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, GREEN, rect)

                                msg = f"Gaste ramase:{self.nrGaste}"
                                crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                                pygame.display.update()
                                print(self)
                        else:  # prima miscare
                            if (linFin, colFin) in self.checkMove(linInit, colInit):  # mutare
                                self.board[linInit][colInit] = "·"
                                self.board[linFin][colFin] = "V"

                                poz = convertToGUI(linInit, colInit, modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, GREEN, rect)

                                poz = convertToGUI(linFin, colFin, modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, RED, rect)

                                self.pozVulpe = (linFin, colFin)
                                playerMoves += 1
                                player = not player

                                msg = f"Gaste ramase:{self.nrGaste}"
                                crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                                pygame.display.update()
                                print(self)
                            elif (linFin, colFin) in ls:  # salt
                                self.board[linInit][colInit] = "·"
                                self.board[linFin][colFin] = "V"

                                poz = convertToGUI(linInit, colInit, modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, GREEN, rect)

                                poz = convertToGUI(linFin, colFin, modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, RED, rect)

                                self.pozVulpe = (linFin, colFin)
                                self.nrGaste -= 1
                                self.board[int(abs(linInit + linFin) / 2)][int(abs(colInit + colFin) / 2)] = "·"

                                poz = convertToGUI(int(abs(linInit + linFin) / 2), int(abs(colInit + colFin) / 2), modifier)
                                rect = Rect(poz[0], poz[1], modifier, modifier)
                                pygame.draw.rect(screen, GREEN, rect)

                                capture = True

                                msg = f"Gaste ramase:{self.nrGaste}"
                                crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                                pygame.display.update()
                                print(self)
                    else:  # gasca
                        msg = "Gastele muta!"
                        crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, GREEN)
                        linInit = 20
                        colInit = 20
                        linFin = 20
                        colFin = 20
                        moveTime = time.time()
                        while True:  # poz init
                            ok = True
                            for event in pygame.event.get():
                                if event.type == QUIT:
                                    pygame.quit()
                                    print(f"Timp minim: {minTime}")
                                    print(f"Timp maxim: {maxTime}")
                                    print(f"Media timpilor:{sum(timeSet) / len(timeSet)}")
                                    timeSet.sort()
                                    print(f"Mediana timpilor: {timeSet[int(len(timeSet) / 2)]}")

                                    print(f"Min noduri generate: {self.nrMinNod}")
                                    print(f"Max noduri generate: {self.nrMaxNod}")
                                    print(f"Media nr de noduri generate: {sum(self.nodSet) / len(self.nodSet)}")
                                    self.nodSet.sort()
                                    print(f"Mediana nr de noduri generate: {self.nodSet[int(len(self.nodSet) / 2)]}")

                                    print(f"Timp de joc:{time.time() - startTime}")

                                    print(f"Nr mutari jucator:{playerMoves} ")
                                    print(f"Nr mutari PC:{computerMoves}")
                                    sys.exit()
                                if event.type == MOUSEBUTTONDOWN:
                                    poz = pygame.mouse.get_pos()
                                    poz = convertFromGUI(poz[0], poz[1], modifier)
                                    if poz[1] < 13 and self.board[poz[0]][poz[1]] == "G":
                                        ok = False
                                        linInit = poz[0]
                                        colInit = poz[1]
                                        break
                            if not ok:
                                break

                        poz = convertToGUI(linInit, colInit, modifier)
                        rect = Rect(poz[0], poz[1], modifier, modifier)
                        pygame.draw.rect(screen, ORANGE, rect)
                        pygame.display.update()

                        while True:  # poz fin
                            ok = True
                            for event in pygame.event.get():
                                if event.type == QUIT:
                                    pygame.quit()
                                    scor = self.evaluate()
                                    print("Ati incheiat jocul!")
                                    print(f"Timp de joc:{time.time() - startTime}")
                                    print(f"Nr mutari jucator:{playerMoves}   Nr mutari PC:{computerMoves}")
                                    sys.exit()
                                if event.type == MOUSEBUTTONDOWN:
                                    poz = pygame.mouse.get_pos()
                                    poz = convertFromGUI(poz[0], poz[1], modifier)
                                    if poz[1] < 13 and (poz[0], poz[1]) in self.checkMove(linInit, colInit) + [(linInit, colInit)]:
                                        ok = False
                                        linFin = poz[0]
                                        colFin = poz[1]
                                        break
                            if not ok:
                                break

                        tGandire = time.time() - moveTime
                        print(f"Timp gandire jucator:{tGandire}")

                        if linFin != linInit or colFin != colInit:
                            player = not player
                            playerMoves += 1
                            self.board[linInit][colInit] = "·"
                            self.board[linFin][colFin] = "G"

                            poz = convertToGUI(linInit, colInit, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, GREEN, rect)

                            poz = convertToGUI(linFin, colFin, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, BLUE, rect)

                            msg = f"Gaste ramase:{self.nrGaste}"
                            crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                            pygame.display.update()
                            print(self)
                        else:  # mutare gresita
                            poz = convertToGUI(linInit, colInit, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, BLUE, rect)
                            pygame.display.update()

            else:
                scor = self.evaluate()
                showMessage(screen, mwidth, modifier, font, "GAME OVER!", 0, maxPoz)

                # afiseaza simboluri castigator
                if scor == MIN:
                    poz = convertToGUI(self.pozVulpe[0], self.pozVulpe[1], modifier)
                    showSymbol(poz[0], poz[1], screen, "V", modifier)
                else:
                    for i in range(13):
                        for j in range(13):
                            if self.board[i][j] == "G":
                                poz = convertToGUI(i, j, modifier)
                                showSymbol(poz[0], poz[1], screen, "G", modifier)
                # afisari connsola
                print(f"Timp minim: {minTime}")
                print(f"Timp maxim: {maxTime}")
                print(f"Media timpilor:{sum(timeSet) / len(timeSet)}")
                timeSet.sort()
                print(f"Mediana timpilor: {timeSet[int(len(timeSet) / 2)]}")

                print(f"Min noduri generate: {self.nrMinNod}")
                print(f"Max noduri generate: {self.nrMaxNod}")
                print(f"Media nr de noduri generate: {sum(self.nodSet) / len(self.nodSet)}")
                self.nodSet.sort()
                print(f"Mediana nr de noduri generate: {self.nodSet[int(len(self.nodSet) / 2)]}")

                print(f"Timp de joc:{time.time() - startTime}")

                print(f"Nr mutari jucator:{playerMoves} ")
                print(f"Nr mutari PC:{computerMoves}")

                # afisare castigator
                if scor == MIN:
                    print("Vulpea castiga!!")
                else:
                    print("Gastele castiga!!")

                # asteapta sa se inchida fereastra
                while True:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()
        # player vs player
        elif self.gameMode == 2:
            startTime = time.time()

            # jucatorul curent, true = gaste
            playerG = True
            playerGmoves = 0
            playerVmoves = 0
            capture = False

            for i in range(13):
                for j in range(13):
                    rect = Rect(j * modifier, i * modifier, modifier, modifier)
                    if self.board[i][j] == "X":
                        pygame.draw.rect(screen, BLACK, rect)
                    elif self.board[i][j] == "V":
                        pygame.draw.rect(screen, RED, rect)
                    elif self.board[i][j] == "G":
                        pygame.draw.rect(screen, BLUE, rect)
                    elif self.board[i][j] == "·":
                        pygame.draw.rect(screen, GREEN, rect)
                    else:
                        pygame.draw.rect(screen, WHITE, rect)
                        poz = convertToGUI(i, j, modifier)
                        showSymbol(poz[0], poz[1], screen, self.board[i][j], modifier)
            font = pygame.font.SysFont('arial', 20)
            pygame.display.update()

            while not self.isEndGame():
                # jucatorul cu Gaste
                if playerG:
                    msg = "Gastele muta!"
                    crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, GREEN)
                    linInit = 20
                    colInit = 20
                    linFin = 20
                    colFin = 20
                    moveTime = time.time()
                    while True:  # poz init
                        ok = True
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                pygame.quit()
                                print(f"Timp de joc:{time.time() - startTime}")
                                print(f"Nr mutari jucator gaste:{playerGmoves} ")
                                print(f"Nr mutari jucator vulpi:{playerVmoves}")
                                sys.exit()
                            if event.type == MOUSEBUTTONDOWN:
                                poz = pygame.mouse.get_pos()
                                poz = convertFromGUI(poz[0], poz[1], modifier)
                                if poz[1] < 13 and self.board[poz[0]][poz[1]] == "G":
                                    ok = False
                                    linInit = poz[0]
                                    colInit = poz[1]
                                    break
                        if not ok:
                            break

                    poz = convertToGUI(linInit, colInit, modifier)
                    rect = Rect(poz[0], poz[1], modifier, modifier)
                    pygame.draw.rect(screen, ORANGE, rect)
                    pygame.display.update()

                    while True:  # poz fin
                        ok = True
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                pygame.quit()
                                print(f"Timp de joc:{time.time() - startTime}")
                                print(f"Nr mutari jucator gaste:{playerGmoves} ")
                                print(f"Nr mutari jucator vulpi:{playerVmoves}")
                                sys.exit()
                            if event.type == MOUSEBUTTONDOWN:
                                poz = pygame.mouse.get_pos()
                                poz = convertFromGUI(poz[0], poz[1], modifier)
                                if poz[1] < 13 and (poz[0], poz[1]) in self.checkMove(linInit, colInit) + [(linInit, colInit)]:
                                    ok = False
                                    linFin = poz[0]
                                    colFin = poz[1]
                                    break
                        if not ok:
                            break

                    tGandire = time.time() - moveTime
                    print(f"Timp gandire jucator:{tGandire}")

                    if linFin != linInit or colFin != colInit:
                        playerG = not playerG
                        playerGmoves += 1
                        self.board[linInit][colInit] = "·"
                        self.board[linFin][colFin] = "G"

                        poz = convertToGUI(linInit, colInit, modifier)
                        rect = Rect(poz[0], poz[1], modifier, modifier)
                        pygame.draw.rect(screen, GREEN, rect)

                        poz = convertToGUI(linFin, colFin, modifier)
                        rect = Rect(poz[0], poz[1], modifier, modifier)
                        pygame.draw.rect(screen, BLUE, rect)

                        msg = f"Gaste ramase:{self.nrGaste}"
                        crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                        pygame.display.update()
                        print(self)
                    else:  # mutare gresita
                        poz = convertToGUI(linInit, colInit, modifier)
                        rect = Rect(poz[0], poz[1], modifier, modifier)
                        pygame.draw.rect(screen, BLUE, rect)
                        pygame.display.update()
                #jucatorul cu Vulpea
                else:
                    msg = "Vulpea muta!"
                    crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                    linInit = self.pozVulpe[0]
                    colInit = self.pozVulpe[1]

                    moveTime = time.time()
                    ls = self.checkCapture(linInit, colInit)
                    if not capture or len(ls) != 0:  # daca poate muta
                        # get user input
                        while True:
                            ok = True
                            for event in pygame.event.get():
                                if event.type == QUIT:
                                    pygame.quit()
                                    print(f"Timp de joc:{time.time() - startTime}")
                                    print(f"Nr mutari jucator gaste:{playerGmoves} ")
                                    print(f"Nr mutari jucator vulpi:{playerVmoves}")
                                    sys.exit()
                                if event.type == MOUSEBUTTONDOWN:
                                    poz = pygame.mouse.get_pos()
                                    poz = convertFromGUI(poz[0], poz[1], modifier)
                                    if poz[1] < 13:
                                        ok = False
                                        linFin = poz[0]
                                        colFin = poz[1]
                                        break
                            if not ok:
                                break
                    tGandire = time.time() - moveTime
                    print(f"Timp gandire jucator:{tGandire}")

                    if capture:  # dupa 1 salt
                        if len(ls) == 0:  # nu mai are unde sa sara
                            capture = False
                            playerG = not playerG
                            playerVmoves += 1
                        elif (linFin, colFin) in ls:  # continua sa sara
                            self.board[linInit][colInit] = "·"
                            self.board[linFin][colFin] = "V"

                            poz = convertToGUI(linInit, colInit, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, GREEN, rect)

                            poz = convertToGUI(linFin, colFin, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, RED, rect)

                            self.pozVulpe = (linFin, colFin)
                            self.nrGaste -= 1

                            self.board[int(abs(linInit + linFin) / 2)][int(abs(colInit + colFin) / 2)] = "·"

                            poz = convertToGUI(int(abs(linInit + linFin) / 2), int(abs(colInit + colFin) / 2), modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, GREEN, rect)

                            msg = f"Gaste ramase:{self.nrGaste}"
                            crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                            pygame.display.update()
                            print(self)
                    else:  # prima miscare
                        if (linFin, colFin) in self.checkMove(linInit, colInit):  # mutare
                            self.board[linInit][colInit] = "·"
                            self.board[linFin][colFin] = "V"

                            poz = convertToGUI(linInit, colInit, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, GREEN, rect)

                            poz = convertToGUI(linFin, colFin, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, RED, rect)

                            self.pozVulpe = (linFin, colFin)
                            playerVmoves += 1
                            playerG = not playerG

                            msg = f"Gaste ramase:{self.nrGaste}"
                            crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                            pygame.display.update()
                            print(self)
                        elif (linFin, colFin) in ls:  # salt
                            self.board[linInit][colInit] = "·"
                            self.board[linFin][colFin] = "V"

                            poz = convertToGUI(linInit, colInit, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, GREEN, rect)

                            poz = convertToGUI(linFin, colFin, modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, RED, rect)

                            self.pozVulpe = (linFin, colFin)
                            self.nrGaste -= 1
                            self.board[int(abs(linInit + linFin) / 2)][int(abs(colInit + colFin) / 2)] = "·"

                            poz = convertToGUI(int(abs(linInit + linFin) / 2), int(abs(colInit + colFin) / 2), modifier)
                            rect = Rect(poz[0], poz[1], modifier, modifier)
                            pygame.draw.rect(screen, GREEN, rect)

                            capture = True

                            msg = f"Gaste ramase:{self.nrGaste}"
                            crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                            pygame.display.update()
                            print(self)
            else:
                scor = self.evaluate()
                showMessage(screen, mwidth, modifier, font, "GAME OVER!", 0, maxPoz)

                if scor == MIN:
                    poz = convertToGUI(self.pozVulpe[0], self.pozVulpe[1], modifier)
                    showSymbol(poz[0], poz[1], screen, "V", modifier)
                else:
                    for i in range(13):
                        for j in range(13):
                            if self.board[i][j] == "G":
                                poz = convertToGUI(i, j, modifier)
                                showSymbol(poz[0], poz[1], screen, "G", modifier)

                print(f"Timp de joc:{time.time() - startTime}")
                print(f"Nr mutari jucator Gaste:{playerGmoves} ")
                print(f"Nr mutari jucator Vulpi:{playerVmoves}")

                if scor == MIN:
                    print("Vulpea castiga!!")
                else:
                    print("Gastele castiga!!")

                while True:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()





def convertFromGUI(x, y, modifier):  # functie utilitara pt a converti pozitie din gui in matrice
    return (y // modifier, x // modifier)  # (nrcol, nrlin)

def convertToGUI(lin, col, modifier):  # functie utilitara pt a converti pozitie din matrice in gui
    return (col * modifier, lin * modifier)

def showMessage(screen, mwidth, modifier, font, msg, position, maxPoz, color=None):
    # functie pt afisare log message in GUI
    if position == 0:  # clear log
        rect = Rect(mwidth, 0, 2 * modifier, maxPoz * 2 * modifier)
        screen.fill(BLACK, rect)

    text = font.render(msg, True, WHITE)

    textRect = text.get_rect()
    # textRect = rect.fit(textRect)

    textRect.center = (mwidth + modifier, modifier // 4 + position * (modifier // 2))

    if color != None:
        textRect.width = modifier * 2
        textRect.height = modifier // 2
        textRect.left = mwidth
        textRect.top = position * (modifier // 2)
        pygame.draw.rect(screen, color, textRect)

    screen.blit(text, textRect)

    pygame.display.update()
    position += 1

    if position == maxPoz:
        return 0
    else:
        return position

def showSymbol(x, y, screen, symbol, modifier):  # functie pt a marca simbolul unui jucator pe gui
    font = pygame.font.SysFont('arial', 50)
    text = font.render(symbol, True, BLACK)
    textRect = text.get_rect()
    textRect.center = (x + modifier // 2, y + modifier // 2)
    screen.blit(text, textRect)
    pygame.display.update()


if __name__ == "__main__":
    newGame = Game()
    newGame.playGUI()
