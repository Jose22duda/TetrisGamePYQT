# Joseph Vusumzi Duda

import random
import sys
from enum import Enum
from typing import List, Tuple, Optional

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QSettings
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
from PyQt5.QtWidgets import (QMainWindow, QFrame, QDesktopWidget, QApplication, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QWidget, QMessageBox, QMenuBar, QAction)


class TetrominoType(Enum):
    """Enum for tetromino types"""
    NO_SHAPE = 0
    Z_SHAPE = 1
    S_SHAPE = 2
    LINE_SHAPE = 3
    T_SHAPE = 4
    SQUARE_SHAPE = 5
    L_SHAPE = 6
    MIRRORED_L_SHAPE = 7


class GameState(Enum):
    """Enum for game states"""
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2
    GAME_OVER = 3


class Tetris(QMainWindow):
    """Main Tetris game window"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('TetrisGame', 'Tetris')
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Enhanced Tetris')
        self.setFixedSize(700, 600)
        self.center_window()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create game board
        self.board = Board(self)
        main_layout.addWidget(self.board)
        
        # Create side panel
        side_panel = self.create_side_panel()
        main_layout.addWidget(side_panel)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusbar = self.statusBar()
        self.board.msg_to_statusbar.connect(self.statusbar.showMessage)
        
        # Connect signals
        self.board.score_changed.connect(self.update_score)
        self.board.level_changed.connect(self.update_level)
        self.board.lines_changed.connect(self.update_lines)
        self.board.next_piece_changed.connect(self.update_next_piece)
        
        self.show()

    def create_side_panel(self) -> QWidget:
        """Create the side panel with game info"""
        panel = QWidget()
        panel.setFixedWidth(200)
        layout = QVBoxLayout(panel)
        
        # Game statistics
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Box)
        stats_layout = QVBoxLayout(stats_frame)
        
        # Score
        self.score_label = QLabel("Score: 0")
        self.score_label.setFont(QFont("Arial", 12, QFont.Bold))
        stats_layout.addWidget(self.score_label)
        
        # Level
        self.level_label = QLabel("Level: 1")
        self.level_label.setFont(QFont("Arial", 12, QFont.Bold))
        stats_layout.addWidget(self.level_label)
        
        # Lines
        self.lines_label = QLabel("Lines: 0")
        self.lines_label.setFont(QFont("Arial", 12, QFont.Bold))
        stats_layout.addWidget(self.lines_label)
        
        layout.addWidget(stats_frame)
        
        # Next piece preview
        next_frame = QFrame()
        next_frame.setFrameStyle(QFrame.Box)
        next_layout = QVBoxLayout(next_frame)
        
        next_title = QLabel("Next Piece")
        next_title.setFont(QFont("Arial", 10, QFont.Bold))
        next_title.setAlignment(Qt.AlignCenter)
        next_layout.addWidget(next_title)
        
        self.next_piece_widget = NextPieceWidget()
        next_layout.addWidget(self.next_piece_widget)
        
        layout.addWidget(next_frame)
        
        # Control buttons
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_game)
        self.pause_button.setEnabled(False)
        layout.addWidget(self.pause_button)
        
        # Controls info
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Box)
        controls_layout = QVBoxLayout(controls_frame)
        
        controls_title = QLabel("Controls")
        controls_title.setFont(QFont("Arial", 10, QFont.Bold))
        controls_title.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(controls_title)
        
        controls_text = """
        ← → : Move
        ↑ : Rotate Left
        ↓ : Rotate Right
        Space : Drop
        P : Pause
        """
        controls_label = QLabel(controls_text)
        controls_label.setFont(QFont("Arial", 8))
        controls_layout.addWidget(controls_label)
        
        layout.addWidget(controls_frame)
        layout.addStretch()
        
        return panel

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # Game menu
        game_menu = menubar.addMenu('Game')
        
        new_game_action = QAction('New Game', self)
        new_game_action.setShortcut('Ctrl+N')
        new_game_action.triggered.connect(self.start_game)
        game_menu.addAction(new_game_action)
        
        game_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)
        


    def center_window(self):
        """Center the window on screen"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def start_game(self):
        """Start a new game"""
        self.board.start()
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.pause_button.setText("Pause")

    def pause_game(self):
        """Pause/resume the game"""
        self.board.pause()
        if self.board.is_paused:
            self.pause_button.setText("Resume")
        else:
            self.pause_button.setText("Pause")

    def update_score(self, score: int):
        """Update the score display"""
        self.score_label.setText(f"Score: {score}")

    def update_level(self, level: int):
        """Update the level display"""
        self.level_label.setText(f"Level: {level}")

    def update_lines(self, lines: int):
        """Update the lines display"""
        self.lines_label.setText(f"Lines: {lines}")

    def update_next_piece(self, piece_type: TetrominoType):
        """Update the next piece preview"""
        self.next_piece_widget.set_piece(piece_type)



    def load_settings(self):
        """Load game settings"""
        # Could load high scores, preferences, etc.
        pass

    def save_settings(self):
        """Save game settings"""
        # Could save high scores, preferences, etc.
        pass

    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        event.accept()


class NextPieceWidget(QWidget):
    """Widget to display the next piece"""
    
    def __init__(self):
        super().__init__()
        self.piece_type = TetrominoType.NO_SHAPE
        self.setFixedSize(80, 80)

    def set_piece(self, piece_type: TetrominoType):
        """Set the piece type to display"""
        self.piece_type = piece_type
        self.update()

    def paintEvent(self, event):
        """Paint the next piece"""
        if self.piece_type == TetrominoType.NO_SHAPE:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get piece shape
        shape = Shape()
        shape.set_shape(self.piece_type)
        
        # Calculate center position
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Draw the piece
        square_size = 15
        for i in range(4):
            x = center_x + shape.x(i) * square_size
            y = center_y + shape.y(i) * square_size
            self.draw_square(painter, x, y, square_size, self.piece_type)

    def draw_square(self, painter: QPainter, x: int, y: int, size: int, shape_type: TetrominoType):
        """Draw a single square"""
        color_map = {
            TetrominoType.Z_SHAPE: QColor(204, 102, 102),
            TetrominoType.S_SHAPE: QColor(102, 204, 102),
            TetrominoType.LINE_SHAPE: QColor(102, 102, 204),
            TetrominoType.T_SHAPE: QColor(204, 204, 102),
            TetrominoType.SQUARE_SHAPE: QColor(204, 102, 204),
            TetrominoType.L_SHAPE: QColor(102, 204, 204),
            TetrominoType.MIRRORED_L_SHAPE: QColor(218, 170, 0)
        }
        
        color = color_map.get(shape_type, QColor(128, 128, 128))
        painter.fillRect(x, y, size, size, color)
        
        # Draw border
        painter.setPen(color.lighter())
        painter.drawRect(x, y, size, size)


class Board(QFrame):
    """Main game board"""
    
    msg_to_statusbar = pyqtSignal(str)
    score_changed = pyqtSignal(int)
    level_changed = pyqtSignal(int)
    lines_changed = pyqtSignal(int)
    next_piece_changed = pyqtSignal(TetrominoType)
    
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 22
    INITIAL_SPEED = 500
    
    def __init__(self, parent):
        super().__init__(parent)
        self.init_board()

    def init_board(self):
        """Initialize the game board"""
        self.timer = QBasicTimer()
        self.is_waiting_after_line = False
        self.cur_x = 0
        self.cur_y = 0
        self.score = 0
        self.level = 1
        self.lines_removed = 0
        self.board = []
        self.cur_piece = Shape()
        self.next_piece = Shape()
        self.game_state = GameState.STOPPED
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.is_started = False
        self.is_paused = False
        self.clear_board()
        
        # Generate first next piece
        self.next_piece.set_random_shape()

    def shape_at(self, x: int, y: int) -> TetrominoType:
        """Get the shape at board position"""
        return self.board[(y * Board.BOARD_WIDTH) + x]

    def set_shape_at(self, x: int, y: int, shape: TetrominoType):
        """Set shape at board position"""
        self.board[(y * Board.BOARD_WIDTH) + x] = shape

    def square_width(self) -> int:
        """Get width of one square"""
        return self.contentsRect().width() // Board.BOARD_WIDTH

    def square_height(self) -> int:
        """Get height of one square"""
        return self.contentsRect().height() // Board.BOARD_HEIGHT

    def start(self):
        """Start a new game"""
        if self.is_paused:
            return

        self.is_started = True
        self.is_paused = False
        self.is_waiting_after_line = False
        self.score = 0
        self.level = 1
        self.lines_removed = 0
        self.game_state = GameState.RUNNING
        
        self.clear_board()
        self.emit_signals()
        self.new_piece()
        self.timer.start(Board.INITIAL_SPEED, self)

    def pause(self):
        """Pause/resume the game"""
        if not self.is_started:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.timer.stop()
            self.msg_to_statusbar.emit("Paused")
            self.game_state = GameState.PAUSED
        else:
            self.timer.start(self.get_speed(), self)
            self.msg_to_statusbar.emit(f"Score: {self.score}")
            self.game_state = GameState.RUNNING

        self.update()

    def get_speed(self) -> int:
        """Calculate game speed based on level"""
        return max(50, Board.INITIAL_SPEED - (self.level - 1) * 50)

    def paintEvent(self, event):
        """Paint the game board"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.contentsRect()
        board_top = rect.bottom() - Board.BOARD_HEIGHT * self.square_height()

        # Draw settled pieces
        for i in range(Board.BOARD_HEIGHT):
            for j in range(Board.BOARD_WIDTH):
                shape = self.shape_at(j, Board.BOARD_HEIGHT - i - 1)
                if shape != TetrominoType.NO_SHAPE:
                    self.draw_square(painter,
                                   rect.left() + j * self.square_width(),
                                   board_top + i * self.square_height(),
                                   shape)

        # Draw current piece
        if self.cur_piece.shape() != TetrominoType.NO_SHAPE:
            for i in range(4):
                x = self.cur_x + self.cur_piece.x(i)
                y = self.cur_y - self.cur_piece.y(i)
                self.draw_square(painter,
                               rect.left() + x * self.square_width(),
                               board_top + (Board.BOARD_HEIGHT - y - 1) * self.square_height(),
                               self.cur_piece.shape())

        # Draw pause overlay
        if self.is_paused:
            painter.fillRect(rect, QColor(0, 0, 0, 128))
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 24, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, "PAUSED")

    def keyPressEvent(self, event):
        """Handle key press events"""
        if not self.is_started or self.cur_piece.shape() == TetrominoType.NO_SHAPE:
            super().keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        if self.is_paused:
            return

        if key == Qt.Key_Left:
            self.try_move(self.cur_piece, self.cur_x - 1, self.cur_y)
        elif key == Qt.Key_Right:
            self.try_move(self.cur_piece, self.cur_x + 1, self.cur_y)
        elif key == Qt.Key_Down:
            self.try_move(self.cur_piece.rotate_right(), self.cur_x, self.cur_y)
        elif key == Qt.Key_Up:
            self.try_move(self.cur_piece.rotate_left(), self.cur_x, self.cur_y)
        elif key == Qt.Key_Space:
            self.drop_down()
        elif key == Qt.Key_D:
            self.one_line_down()
        else:
            super().keyPressEvent(event)

    def timerEvent(self, event):
        """Handle timer events"""
        if event.timerId() == self.timer.timerId():
            if self.is_waiting_after_line:
                self.is_waiting_after_line = False
                self.new_piece()
            else:
                self.one_line_down()
        else:
            super().timerEvent(event)

    def clear_board(self):
        """Clear the game board"""
        self.board = [TetrominoType.NO_SHAPE] * (Board.BOARD_HEIGHT * Board.BOARD_WIDTH)

    def drop_down(self):
        """Drop piece to bottom"""
        new_y = self.cur_y
        while new_y > 0:
            if not self.try_move(self.cur_piece, self.cur_x, new_y - 1):
                break
            new_y -= 1
        self.piece_dropped()

    def one_line_down(self):
        """Move piece down one line"""
        if not self.try_move(self.cur_piece, self.cur_x, self.cur_y - 1):
            self.piece_dropped()

    def piece_dropped(self):
        """Handle piece being dropped"""
        for i in range(4):
            x = self.cur_x + self.cur_piece.x(i)
            y = self.cur_y - self.cur_piece.y(i)
            self.set_shape_at(x, y, self.cur_piece.shape())

        self.remove_full_lines()

        if not self.is_waiting_after_line:
            self.new_piece()

    def remove_full_lines(self):
        """Remove completed lines"""
        rows_to_remove = []

        for i in range(Board.BOARD_HEIGHT):
            if all(self.shape_at(j, i) != TetrominoType.NO_SHAPE 
                   for j in range(Board.BOARD_WIDTH)):
                rows_to_remove.append(i)

        if not rows_to_remove:
            return

        # Remove rows from bottom to top
        for row in reversed(rows_to_remove):
            for k in range(row, Board.BOARD_HEIGHT - 1):
                for l in range(Board.BOARD_WIDTH):
                    self.set_shape_at(l, k, self.shape_at(l, k + 1))

        num_lines = len(rows_to_remove)
        self.lines_removed += num_lines
        
        # Update score based on lines cleared
        line_scores = {1: 40, 2: 100, 3: 300, 4: 1200}
        self.score += line_scores.get(num_lines, 0) * self.level
        
        # Update level
        self.level = (self.lines_removed // 10) + 1
        
        self.emit_signals()
        self.is_waiting_after_line = True
        self.cur_piece.set_shape(TetrominoType.NO_SHAPE)
        self.timer.start(self.get_speed(), self)
        self.update()

    def new_piece(self):
        """Create a new piece"""
        self.cur_piece = self.next_piece
        self.next_piece = Shape()
        self.next_piece.set_random_shape()
        self.next_piece_changed.emit(self.next_piece.shape())
        
        self.cur_x = Board.BOARD_WIDTH // 2 + 1
        self.cur_y = Board.BOARD_HEIGHT - 1 + self.cur_piece.min_y()

        if not self.try_move(self.cur_piece, self.cur_x, self.cur_y):
            self.cur_piece.set_shape(TetrominoType.NO_SHAPE)
            self.timer.stop()
            self.is_started = False
            self.game_state = GameState.GAME_OVER
            self.msg_to_statusbar.emit("Game Over")

    def try_move(self, new_piece: 'Shape', new_x: int, new_y: int) -> bool:
        """Try to move a piece"""
        for i in range(4):
            x = new_x + new_piece.x(i)
            y = new_y - new_piece.y(i)

            if (x < 0 or x >= Board.BOARD_WIDTH or 
                y < 0 or y >= Board.BOARD_HEIGHT):
                return False

            if self.shape_at(x, y) != TetrominoType.NO_SHAPE:
                return False

        self.cur_piece = new_piece
        self.cur_x = new_x
        self.cur_y = new_y
        self.update()
        return True

    def draw_square(self, painter: QPainter, x: int, y: int, shape: TetrominoType):
        """Draw a single square"""
        color_map = {
            TetrominoType.Z_SHAPE: QColor(204, 102, 102),
            TetrominoType.S_SHAPE: QColor(102, 204, 102),
            TetrominoType.LINE_SHAPE: QColor(102, 102, 204),
            TetrominoType.T_SHAPE: QColor(204, 204, 102),
            TetrominoType.SQUARE_SHAPE: QColor(204, 102, 204),
            TetrominoType.L_SHAPE: QColor(102, 204, 204),
            TetrominoType.MIRRORED_L_SHAPE: QColor(218, 170, 0)
        }
        
        color = color_map.get(shape, QColor(128, 128, 128))
        
        # Fill the square
        painter.fillRect(x + 1, y + 1, 
                        self.square_width() - 2, 
                        self.square_height() - 2, color)

        # Draw 3D effect
        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.square_height() - 1, x, y)
        painter.drawLine(x, y, x + self.square_width() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.square_height() - 1,
                        x + self.square_width() - 1, y + self.square_height() - 1)
        painter.drawLine(x + self.square_width() - 1,
                        y + self.square_height() - 1, 
                        x + self.square_width() - 1, y + 1)

    def emit_signals(self):
        """Emit status signals"""
        self.score_changed.emit(self.score)
        self.level_changed.emit(self.level)
        self.lines_changed.emit(self.lines_removed)


class Shape:
    """Tetris piece shape"""
    
    COORDS_TABLE = {
        TetrominoType.NO_SHAPE: ((0, 0), (0, 0), (0, 0), (0, 0)),
        TetrominoType.Z_SHAPE: ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        TetrominoType.S_SHAPE: ((0, -1), (0, 0), (1, 0), (1, 1)),
        TetrominoType.LINE_SHAPE: ((0, -1), (0, 0), (0, 1), (0, 2)),
        TetrominoType.T_SHAPE: ((-1, 0), (0, 0), (1, 0), (0, 1)),
        TetrominoType.SQUARE_SHAPE: ((0, 0), (1, 0), (0, 1), (1, 1)),
        TetrominoType.L_SHAPE: ((-1, -1), (0, -1), (0, 0), (0, 1)),
        TetrominoType.MIRRORED_L_SHAPE: ((1, -1), (0, -1), (0, 0), (0, 1))
    }

    def __init__(self):
        self.coords = [[0, 0] for _ in range(4)]
        self.piece_shape = TetrominoType.NO_SHAPE

    def shape(self) -> TetrominoType:
        """Get the shape type"""
        return self.piece_shape

    def set_shape(self, shape: TetrominoType):
        """Set the shape type"""
        table = Shape.COORDS_TABLE[shape]
        for i in range(4):
            self.coords[i] = list(table[i])
        self.piece_shape = shape

    def set_random_shape(self):
        """Set a random shape"""
        shapes = list(TetrominoType)[1:]  # Exclude NO_SHAPE
        self.set_shape(random.choice(shapes))

    def x(self, index: int) -> int:
        """Get x coordinate of point"""
        return self.coords[index][0]

    def y(self, index: int) -> int:
        """Get y coordinate of point"""
        return self.coords[index][1]

    def set_x(self, index: int, x: int):
        """Set x coordinate of point"""
        self.coords[index][0] = x

    def set_y(self, index: int, y: int):
        """Set y coordinate of point"""
        self.coords[index][1] = y

    def min_x(self) -> int:
        """Get minimum x coordinate"""
        return min(self.coords[i][0] for i in range(4))

    def max_x(self) -> int:
        """Get maximum x coordinate"""
        return max(self.coords[i][0] for i in range(4))

    def min_y(self) -> int:
        """Get minimum y coordinate"""
        return min(self.coords[i][1] for i in range(4))

    def max_y(self) -> int:
        """Get maximum y coordinate"""
        return max(self.coords[i][1] for i in range(4))

    def rotate_left(self) -> 'Shape':
        """Rotate shape counter-clockwise"""
        if self.piece_shape == TetrominoType.SQUARE_SHAPE:
            return self

        result = Shape()
        result.piece_shape = self.piece_shape
        for i in range(4):
            result.set_x(i, self.y(i))
            result.set_y(i, -self.x(i))
        return result

    def rotate_right(self) -> 'Shape':
        """Rotate shape clockwise"""
        if self.piece_shape == TetrominoType.SQUARE_SHAPE:
            return self

        result = Shape()
        result.piece_shape = self.piece_shape
        for i in range(4):
            result.set_x(i, -self.y(i))
            result.set_y(i, self.x(i))
        return result


def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Tetris")
    app.setOrganizationName("TetrisGame")
    
    tetris = Tetris()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()