import pygame
from sudoku_board_reader import SudokuBoardReader
from threading import Thread

SCREEN_SIZE = 750
CELL_GAP = 2
BLOCK_GAP = 3
OUTLINE_WIDTH = CELL_GAP+BLOCK_GAP


class Game:
    def __init__(self, screen_size):
        self.board = Board()
        self.board_reader = SudokuBoardReader()
        self.cell_size = (screen_size - (self.board.size + 2) * CELL_GAP) // self.board.size
        self.font = pygame.font.Font(size=50)
        self.selected_cell = False
        self.selected_cell_index = None
        self.outline_rect = None

    def clear_outline(self):
        if self.outline_rect:
            pygame.draw.rect(window, (0, 0, 0), self.outline_rect, width=OUTLINE_WIDTH)

    def mouse_click(self, pos):
        if self.selected_cell:
            self.clear_outline()
        else:
            self.selected_cell = True
        row = pos[1]//self.cell_size
        column = pos[0]//self.cell_size
        self.selected_cell_index = (row, column)

    def place_number(self, number):
        if not self.selected_cell:
            return
        if self.board.place(number, self.selected_cell_index[0], self.selected_cell_index[1]):
            self.clear_outline()
            self.selected_cell = False

    def erase(self):
        self.board.erase(self.selected_cell_index[0], self.selected_cell_index[1])

    def get_board_from_image(self):
        self.board_reader.load_image_file()
        if self.board_reader.loaded:
            self.board.load(self.board_reader.board)

    def solver(self):
        row, column = self.board.find_empty()
        if row == -1:
            return True
        self.selected_cell_index = (row, column)
        for number in range(1, 10):
            if self.board.place(number, row, column):
                self.clear_outline()
                if self.solver():
                    return True
                self.selected_cell_index = (row, column)
        self.board.erase(row, column)
        return False


    def solve(self):
        if self.selected_cell:
            self.clear_outline()
        else:
            self.selected_cell = True
        Thread(target=self.solver, daemon=True).start()


    def draw(self):
        y = 0
        for row in range(self.board.size):
            x = 0
            if row % 3 == 0:
                y += BLOCK_GAP
            for column in range(self.board.size):
                if column % 3 == 0:
                    x += BLOCK_GAP
                number = str(self.board.content[row][column])
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                if self.selected_cell:
                    if row == self.selected_cell_index[0] and column == self.selected_cell_index[1]:
                        self.outline_rect = cell_rect.inflate(OUTLINE_WIDTH, OUTLINE_WIDTH)
                pygame.draw.rect(window, (255, 255, 255), cell_rect)
                if number != '0':
                    text_surface = self.font.render(number, True, (0, 0, 0))
                    window.blit(text_surface, text_surface.get_rect(center=cell_rect.center))
                x += self.cell_size + CELL_GAP
            y += self.cell_size + CELL_GAP
        if self.selected_cell:
            pygame.draw.rect(window, (255, 0, 0), self.outline_rect, width=OUTLINE_WIDTH)


class Board:
    def __init__(self):
        self.size = 9
        self.content = [[0 for _ in range(self.size)] for _ in range(self.size)]

    def load(self, board):
        if len(board) == self.size*self.size:
            self.content = [board[i:i+self.size] for i in range(0, self.size*self.size, self.size)]

    def place(self, number, row, column):
        if self.is_valid(number, row, column):
            self.content[row][column] = number
            return True
        return False

    def is_valid(self, number, selected_row, selected_column):
        for column in range(self.size):
            if self.content[selected_row][column] == number:
                return False
        for row in range(self.size):
            if self.content[row][selected_column] == number:
                return False
        block_row = selected_row // 3
        block_column = selected_column // 3
        for i in range(3*block_row, 3*(block_row+1)):
            for j in range(3*block_column, 3*(block_column+1)):
                if self.content[i][j] == number:
                    return False
        return True

    def find_empty(self):
        for row in range(self.size):
            for column in range(self.size):
                if self.content[row][column] == 0:
                    return row, column
        return -1, -1

    def erase(self, row, column):
        self.content[row][column] = 0

pygame.init()
window = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

clock = pygame.Clock()
game = Game(SCREEN_SIZE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                game.mouse_click(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.unicode.isdigit():
                game.place_number(int(event.unicode))
            elif event.key == pygame.K_TAB:
                game.solve()
            elif event.key == pygame.K_q:
                game.get_board_from_image()
            elif event.key == pygame.K_BACKSPACE:
                game.erase()
    game.draw()
    pygame.display.update()
    clock.tick(60)

pygame.quit()