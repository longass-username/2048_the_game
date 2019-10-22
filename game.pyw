from typing import List, Dict, Any, Union, Generator, Tuple
from random import randint, choice
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


class Window(QMainWindow):

    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()

        self.board = Board(self)
        self.setCentralWidget(self.board)

        self.statusbar = self.statusBar()
        self.board.statusbar_msg[str].connect(self.statusbar.showMessage)

        self.setFixedSize(400, 400)
        self.setWindowTitle('2048')
        self.show()


class Board(QFrame):
    score: int
    spacer: int
    max_val: int
    can_move: bool
    game_over: bool
    direction: str
    status_bar: int
    field_format: int
    cells: List[List[int]]
    end_move_tuple: Tuple[int, ...]
    converted_field: List[List[int]]
    start_move_tuple: Tuple[int, ...]
    color_of_cell: Dict[Union[str, Any], Union[int, Any]]

    statusbar_msg = pyqtSignal(str)

    def __init__(self, parent):
        # noinspection PyArgumentList
        super().__init__(parent=parent)
        self.setup_vars()
        self.setFocusPolicy(Qt.StrongFocus)

    def setup_vars(self):
        self.score = 0
        self.spacer = 3
        self.max_val = 2048
        self.can_move = True
        self.field_format = 4  # this var defines number of rows and columns

        self.color_of_cell = {
            '2': 0x666699,
            '4': 0x75709e,
            '8': 0x857aa3,
            '16': 0x9485a8,
            '32': 0xa38fad,
            '64': 0xb299b2,
            '128': 0xc2a3b8,
            '256': 0xd1adbd,
            '512': 0xe0b8c2,
            '1024': 0xf0c2c7,
            '2048': 0xffcccc
        }
        self.cells = [[0 for j in range(self.field_format)] for i in range(self.field_format)]
        self.statusbar_msg.emit('Score: {}'.format(str(self.score)))
        self.cells_filler(); self.cells_filler()

    def cells_filler(self):
        x = randint(0, self.field_format-1)
        y = randint(0, self.field_format-1)

        if self.have_space_for_new_cell():
            if self.cells[x][y] != 0:
                return self.cells_filler()
            else:
                self.cells[x][y] = choice([2, 4])

    def have_space_for_new_cell(self):
        for row in self.cells:
            if 0 in row:
                return True
        return False

    def field_converter(self, key_pressed):
        self.direction = key_pressed
        converted_field = []

        self.start_move_tuple = tuple(self.get_current_position_tuple())

        if key_pressed == 'LEFT':
            converted_field = self.cells
        elif key_pressed == 'RIGHT':
            for row in self.cells:
                row_copy = row; row_copy.reverse()
                converted_field.append(row_copy)
        elif key_pressed == 'UP':
            zipped_cells = zip(*self.cells)
            for row in list(zipped_cells):
                converted_field.append(list(row))
            converted_field.reverse()
        elif key_pressed == 'DOWN':
            zipped_cells = zip(*self.cells)
            for row in list(zipped_cells):
                row_copy = list(row); row_copy.reverse()
                converted_field.append(row_copy)
            converted_field.reverse()
        self.cell_summ_and_move(converted_field)

    def cell_summ_and_move(self, field):
        for y in range(self.field_format):
            num_of_moves = 0
            for x in range(self.field_format):
                if field[y][x] == 0:
                    num_of_moves += 1
                else:
                    for z in range(x+1, self.field_format):
                        if field[y][x] == field[y][z]:
                            self.score += field[y][x]
                            field[y][x] *= 2
                            field[y][z] = 0
                            break
                        elif field[y][x] != field[y][z] and field[y][z] != 0:
                            break
                    if num_of_moves != 0:
                        field[y][x-num_of_moves] = field[y][x]
                        field[y][x] = 0
        self.field_correcter(field)

    def field_correcter(self, field):
        result = []
        if self.direction == 'LEFT':
            result = field
        elif self.direction == 'RIGHT':
            for row in field:
                row_copy = row; row_copy.reverse()
                result.append(row_copy)
        elif self.direction == 'UP':
            zipped_cells = zip(*field)
            for row in list(zipped_cells):
                row_copy = list(row); row_copy.reverse()
                result.append(row_copy)
        elif self.direction == 'DOWN':
            zipped_cells = zip(*field)
            for row in list(zipped_cells):
                row_copy = list(row); row_copy.reverse()
                result.append(row_copy)
            result.reverse()

        self.cells = result
        self.end_move_tuple = tuple(self.get_current_position_tuple())

        if self.start_move_tuple != self.end_move_tuple:
            self.cells_filler()

        self.game_over = self.is_game_over()
        if self.game_over:
            self.can_move = False
            self.statusbar_msg.emit('Score: {}'.format(str(self.score)))
            self.update()
            self.repeat_msg_box()

        else:
            self.can_move = True
            self.statusbar_msg.emit('Score: {}'.format(str(self.score)))
            self.update()

    def draw_cell(self, painter, x, y, color, number):
        painter.fillRect(y + self.spacer,
                         x + self.spacer,
                         self.square_width() - (self.spacer * 2),
                         self.square_height() - (self.spacer * 2),
                         color)

        painter.setPen(QColor(0x262626))
        painter.setFont(QFont('Decorative', 25))
        painter.drawText(QRect(QPoint(y, x), QSize(self.square_height(), self.square_width())),
                         Qt.AlignCenter,
                         number)

    def paintEvent(self, event):
        painter = QPainter(self)

        for y in range(self.field_format):
            for x in range(self.field_format):
                if self.cells[x][y] != 0:
                    self.draw_cell(painter,
                                   x * self.square_height(),
                                   y * self.square_width(),
                                   QColor(self.color_of_cell[str(self.cells[x][y])]),
                                   str(self.cells[x][y]))

    def keyPressEvent(self, event):
        if self.can_move:
            key = event.key()
            self.can_move = False

            if key == Qt.Key_Left:
                self.field_converter('LEFT')
            elif key == Qt.Key_Right:
                self.field_converter('RIGHT')
            elif key == Qt.Key_Down:
                self.field_converter('DOWN')
            elif key == Qt.Key_Up:
                self.field_converter('UP')

    def is_game_over(self):
        for row in self.cells:
            if self.max_val in row:
                return True

        for row in self.cells:
            if 0 in row:
                return False

        for j in range(self.field_format):
            for i in range(self.field_format):
                if i != (self.field_format - 1):
                    if self.cells[j][i] == self.cells[j][i+1]:
                        return False
                if i != (self.field_format - 1):
                    if self.cells[i][j] == self.cells[i+1][j]:
                        return False
        return True

    def get_current_position_tuple(self):
        return (num for rows in self.cells for num in rows)

    def repeat_msg_box(self):
        reply = QMessageBox.question(self, 'Message',
                                     "-----GAME OVER-----\n\nYour score - {}\nDo you want to replay?".format(self.score), QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.setup_vars()
        else:
            qApp.quit()

    def square_width(self):
        return self.contentsRect().width() / self.field_format

    def square_height(self):
        return self.contentsRect().height() / self.field_format


if __name__ == "__main__":
    game = QApplication(sys.argv)
    window = Window()
    sys.exit(game.exec_())
