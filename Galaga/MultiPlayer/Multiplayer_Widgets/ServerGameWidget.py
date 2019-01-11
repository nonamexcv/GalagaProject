from PyQt5.QtGui import QMovie, QPainter
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from Galaga.MultiPlayer.Scripts.command_parser import CommandParser
from Galaga.MultiPlayer.Scripts.multiplayer_print_modifier import MultiplayerPrintModifier
from Galaga.MultiPlayer.Scripts.multiplayer_move_modifier import MultiplayerMoveModifer
from Galaga.MultiPlayer.multiplayer_gameplay import Gameplay
from Galaga.Scripts.key_notifier import KeyNotifier
from Galaga.Scripts.projectile_modifier import ProjectileModifier


class ServerMainWindow(QWidget):

    move_player_signal = pyqtSignal(int, int)
    command_parser = CommandParser()

    def __init__(self, parent=None):
        super(ServerMainWindow, self).__init__(parent)
        self.start_command_parser()

    @pyqtSlot(int)
    def start_game(self, number_of_players):
        self.setGeometry(0, 0, 800, 600)
        self.setFixedSize(800, 600)

        self.start_ui_window(number_of_players)
        self.start_gameplay(number_of_players)
        self.start_key_notifier()

        #set gif animation
        self.movie = QMovie("img/space-background.gif")
        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()

        #set avatars and projectile
        self.start_player_movement()

    def start_player_movement(self):
        self.player_movement = MultiplayerMoveModifer(self.Window.local_enemy_list, self.Window, self.gameplay)
        self.player_movement.create_projectile_signal.connect(self.Window.print_projectile)
        self.player_movement.move_enemy_signal.connect(self.Window.move_enemy)
        self.player_movement.move_player_signal(self.Window.move_player)
        self.move_player_signal.connect(self.player_movement.move_player)
        self.player_movement.daemon = True
        self.player_movement.start()

    def start_key_notifier(self):
        self.key_notifier = KeyNotifier()
        self.key_notifier.key_signal.connect(self.__update_position__)
        self.key_notifier.start()

    def start_gameplay(self, number_of_players):
        self.gameplay = Gameplay(number_of_players)
        self.gameplay.next_level_signal.connect(self.Window.new_level)
        self.gameplay.player_killed_signal.connect(self.Window.remove_player)
        self.gameplay.daemon = True
        self.gameplay.start()

    def start_command_parser(self):
        self.command_parser.start_game_signal.connect(self.start_game)
        self.command_parser.daemon = True
        self.command_parser.start()

    def start_ui_window(self, number_of_players):
        self.Window = MultiplayerPrintModifier(number_of_players)
        self.setWindowTitle("PyGalaga")
        self.show()

    def paintEvent(self, event):
        current_frame = self.movie.currentPixmap()
        frame_rect = current_frame.rect()
        frame_rect.moveCenter(self.rect().center())
        if frame_rect.intersects(event.rect()):
            painter = QPainter(self)
            painter.drawPixmap(frame_rect.left(), frame_rect.top(), current_frame)

    def closeEvent(self, event):
        self.key_notifier.die()

    def keyPressEvent(self, event):
        self.key_notifier.add_key(event.key())

    def keyReleaseEvent(self, event):
        self.key_notifier.rem_key(event.key())

    def __update_position__(self, key):
        self.move_player_signal.emit(key)
