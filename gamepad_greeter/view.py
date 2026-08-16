import pygame

from pygame import Surface
from pygame.event import Event
from ui import UserSelection, GamepadLegend, GlassPane, PasswordInput
from abc import abstractmethod
from pathlib import Path

class GameView:
    @abstractmethod
    def init(self) -> None: ...
    @abstractmethod
    def handle_event(self, event : Event) -> None: ...
    @abstractmethod
    def update(self, surface_width : int, surface_height : int) -> None: ...
    @abstractmethod
    def draw(self, surface : Surface) -> None: ...

class UserView(GameView):
    LEFT_STICK_THRESHOLD = 0.5

    def __init__(self, users : list[str]):
        self._users = users

        self._left_stick_moved = False

        self._selection : UserSelection = None
        
        self.confirmation_callable : callable[[str], None]

    def handle_event(self, event : Event) -> None:
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0: 
                self.__confirm()

            # PS5 DPad Left
            elif event.button == 13:
                self.__navigate_previous()
            
            #PS5 DPad Right
            elif event.button == 14:
                self.__navigate_next()

        elif event.type == pygame.JOYAXISMOTION:
            # Left stick horizontal
            if event.axis == 0:
                if event.value > self.LEFT_STICK_THRESHOLD:
                    if not self._left_stick_moved:
                        self.__navigate_next()
                        self._left_stick_moved = True

                elif event.value < -self.LEFT_STICK_THRESHOLD:
                    if not self._left_stick_moved:
                        self.__navigate_previous()
                        self._left_stick_moved = True

                elif event.value < self.LEFT_STICK_THRESHOLD:
                    self._left_stick_moved = False

        elif event.type == pygame.JOYHATMOTION:
            x = event.value[0]
            if x == -1: # DPad Left
                self.__navigate_previous()
            elif x == 1: # DPad Right
                self.__navigate_next()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.__navigate_previous()

            elif event.key == pygame.K_RIGHT:
                self.__navigate_next()

            elif event.key == pygame.K_RETURN:
                    self.__confirm()

    def init(self) -> None:
        self._selection = UserSelection(self._users)

    def update(self, surface_width : int, surface_height : int) -> None:
        self._selection.update(surface_width, surface_height)

    def draw(self, surface : Surface) -> None:
        self._selection.draw(surface)

    def __confirm(self) -> None:
        user = self._selection.get_selected_user()

        if self.confirmation_callable:
            self.confirmation_callable(user)

    def __navigate_previous(self) -> None:
        self._selection.navigate_previous()

    def __navigate_next(self) -> None:
        self._selection.navigate_next()

class PasswordView(GameView):
    FONT_PATH =  Path(__file__).parent / "assets" / "fonts" / "dejavu" / "DejaVuSans-Bold.ttf"
    TEXT_COLOR = (255, 255, 255)

    def __init__(self):
        self.__password_buffer = ""

        self.__legend : GamepadLegend = None
        self.__glass_pane = GlassPane(600, 400)
        self.__password_input = PasswordInput(550, 50)
        self.__icon_radius = 75
        self.__font_icon : pygame.font.Font = None
        self.__font_name : pygame.font.Font = None

        self.user_name = ""
        self.confirmation_callable : callable[[str], bool]
        self.exit_callable : callable[[], None]

    def init(self) -> None:
        self.__font_icon = pygame.font.Font(self.FONT_PATH, 72)
        self.__font_name = pygame.font.Font(self.FONT_PATH, 48)
        self.__legend = GamepadLegend()

    def handle_event(self, event : Event):
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0: 
                self.__confirm()

            elif event.button == 1:
                self.__back()

            elif event.button == 2:
                self.__append_password("0")

            elif event.button == 3:
                self.__append_password("9")

            # Left shoulder 8bitdo
            elif event.button == 4:
                self.__append_password("7")

            # Right shoulder 8bitdo
            elif event.button == 5:
                self.__append_password("5")

            # Left shoulder PS5
            elif event.button == 9:
                self.__append_password("7")

            # Right shoulder PS5
            elif event.button == 10:
                self.__append_password("5")
            
            # PS5 DPad Up
            elif event.button == 11:
                self.__append_password("2")
            
            #PS5 DPad Down
            elif event.button == 12:
                self.__append_password("4")

            #PS5 DPad Left
            elif event.button == 13:
                self.__append_password("1")

            #PS5 DPad Right
            elif event.button == 14:
                self.__append_password("3")

            else:
                print(event.button)

        if event.type == pygame.JOYHATMOTION:
            x,y = event.value
            if y == 1: # DPad Up
                self.__append_password("2")
            elif y == -1: # DPad Down
                self.__append_password("4")
            elif x == 1: # DPad Right
                self.__append_password("3")
            elif x == -1: # DPad Left
                self.__append_password("1")

        if event.type == pygame.JOYAXISMOTION:
            
            # Left trigger (L2)
            if event.axis == 4 and event.value == 1.0:
                self.__append_password("8")

            # Right trigger (R2)
            elif event.axis == 5 and event.value == 1.0:
                self.__append_password("6")


        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0: 
                self.__confirm()

        # Keyboard fallback to allow higher password complexity
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.__back()

            elif event.key == pygame.K_RETURN:
                self.__confirm()

            elif event.unicode and event.unicode.isprintable():
                key_name = chr(event.key)
                self.__append_password(key_name)

    def update(self, surface_width : int, surface_height : int) -> None:
        self.__password_input.password_length = len(self.__password_buffer)

        legend_height = self.__legend.get_height()

        self.__legend.pos_x = 40
        self.__legend.pos_y = surface_height - legend_height - 40

        self.__glass_pane.pos_x = (surface_width - self.__glass_pane.width) // 2
        self.__glass_pane.pos_y = (surface_height - self.__glass_pane.height) // 2

        self.__password_input.pos_x = self.__glass_pane.pos_x + 25
        self.__password_input.pos_y = self.__glass_pane.pos_y + self.__glass_pane.height - 75

    def draw(self, surface : Surface) -> None:
        content_center_x = self.__glass_pane.pos_x + self.__glass_pane.width // 2
        icon_center_y = self.__glass_pane.pos_y + self.__glass_pane.height // 4
        pygame.draw.circle(surface, (255, 87, 34), (content_center_x, icon_center_y), self.__icon_radius)

        if self.user_name is not None and len(self.user_name) > 0:
            initial = self.__font_icon.render(self.user_name[0], True, self.TEXT_COLOR)
            surface.blit(initial, initial.get_rect(center=(content_center_x, icon_center_y)))

            name_center_y = self.__glass_pane.pos_y + self.__glass_pane.height * 2 // 3
            name = self.__font_name.render(self.user_name, True, self.TEXT_COLOR)
            surface.blit(name, name.get_rect(center=(content_center_x, name_center_y)))

        self.__glass_pane.draw(surface)
        self.__password_input.draw(surface)
        self.__legend.draw(surface)

    def __append_password(self, character : str) -> None:
        self.__password_buffer = self.__password_buffer + character

    def __back(self) -> None:
        if len(self.__password_buffer) > 0:
            self.__password_buffer = self.__password_buffer[:-1]
            return
        
        self.__password_buffer = ""
        self.__password_input.password_length = 0

        if self.exit_callable:
            self.exit_callable()

    def __confirm(self) -> None:
        pass_input = self.__password_buffer
        self.__password_buffer = ""
        self.__password_input.password_length = 0

        if (self.confirmation_callable):
            success = self.confirmation_callable(pass_input)

            if not success:
                print("Could not log in")