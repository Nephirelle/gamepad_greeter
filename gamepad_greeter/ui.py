import pygame

from pygame.surface import Surface
from pathlib import Path

class UserSelection():
    MAX_USER_PANE_WIDTH = 220
    MAX_USER_PANE_HEIGHT = 280
    HALF_MAX_USER_PANE_WIDTH = 110
    HALF_MAX_USER_PANE_HEIGHT = 140
    MIN_USER_PANE_WIDTH = 120
    MIN_USER_PANE_HEIGHT = 120

    def __init__(self, users : list[str]):
        self.__users = users
        self.__selected_index = 0
        self.__current_scroll = 0.0

        self.__user_panes : list[UserPane] = []

        for user in self.__users:
            user_pane = UserPane(self.MIN_USER_PANE_WIDTH, 
                                 self.MIN_USER_PANE_HEIGHT, 
                                 self.MAX_USER_PANE_WIDTH, 
                                 self.MAX_USER_PANE_HEIGHT, user)
            self.__user_panes.append(user_pane)
            
    def update(self, surface_width : int, surface_height : int) -> None:
        target_scroll = self.__selected_index * self.MAX_USER_PANE_WIDTH
        self.__current_scroll += (target_scroll - self.__current_scroll) * 0.1
        
        center_x = surface_width // 2
        center_y = surface_height // 2

        pane : UserPane
        for i, pane in enumerate(self.__user_panes):
            offset = i * self.MAX_USER_PANE_WIDTH - self.__current_scroll
                        
            # Distance to the center of the screen
            dist = abs(offset)
            # More than one MAX_USER_PANE_WIDTH away: Fully collapsed
            factor = min(1.0, dist / self.MAX_USER_PANE_WIDTH) 

            pane_x = center_x - self.HALF_MAX_USER_PANE_WIDTH + offset
            pane_y = center_y - self.HALF_MAX_USER_PANE_HEIGHT

            pane.set_collapse_factor(factor)
            pane.pos_x = pane_x
            pane.pos_y = pane_y
            pane.update()

    def draw(self, surface : Surface) -> None:
        pane : UserPane
        for pane in self.__user_panes:
            pane.draw(surface)  

    def navigate_next(self) -> None:
        if len(self.__users) > self.__selected_index + 1:
            self.__selected_index += 1

    def navigate_previous(self) -> None:
        if self.__selected_index > 0:
            self.__selected_index -= 1

    def get_selected_index(self) -> int:
        return self.__selected_index

    def get_selected_user(self) -> str:
        return self.__users[self.__selected_index]

class UserPane():
    FONT_PATH =  Path(__file__).parent / "assets" / "fonts" / "dejavu" / "DejaVuSans-Bold.ttf"
    TEXT_COLOR = (255, 255, 255)

    def __init__(self, min_width : int, min_height : int, max_width : int, max_height : int, user_name : str):
        if min_width >= max_width:
            raise Exception("max_width must be greater than min_width.")

        if min_height >= max_height:
            raise Exception("max_height must be greater that min_height.")

        self.pos_x = 0
        self.pos_y = 0

        self.user_name = user_name

        self._min_width = min_width
        self._min_height = min_height

        self._max_width = max_width
        self._max_height = max_height

        min_square = min(min_width, min_height)
        self._padding = 15
        self._icon_radius = (min_square - self._padding * 2) // 2
        self._icon_center_x = max_width // 2 # Always centered horizontally
        self._icon_center_y = self._padding # Can be moved up and down depending on expand factor

        self._glass_pane = GlassPane()

        self._font_name = pygame.font.Font(self.FONT_PATH, 30)
        self._font_icon = pygame.font.Font(self.FONT_PATH, 40)
        self._name_alpha = 1
        self._name_center_x = self._icon_center_x
        self._name_center_y = self._max_height * 3 // 4

        self.__collapse_factor = 1.0

    def set_collapse_factor(self, factor : float) -> None:
        if factor < 0.0 or factor > 1.0:
            raise Exception("Invalid factor")

        self.__collapse_factor = factor

    def get_collapse_factor(self) -> float:
        return self.__collapse_factor

    def update(self) -> None:
        actual_width = self._max_width - (self._max_width - self._min_width) * self.__collapse_factor
        actual_height = self._max_height - (self._max_height - self._min_height) * self.__collapse_factor

        self._glass_pane.width = actual_width
        self._glass_pane.height = actual_height
        self._glass_pane.pos_x = (self._max_width - actual_width) // 2
        self._glass_pane.pos_y = (self._max_height - actual_height) // 2

        self._icon_center_y = self._max_height / 2 - self._icon_radius * (1.0 - self.__collapse_factor)

        self._name_alpha = max(0, int((1.0 - self.__collapse_factor * 1.5) * 255))

    def draw(self, surface : Surface) -> None:
        pane = pygame.Surface((self._max_width, self._max_height), pygame.SRCALPHA)

        self._glass_pane.draw(pane)
        
        pygame.draw.circle(pane, (255, 87, 34), (self._icon_center_x, self._icon_center_y), self._icon_radius)

        if self.user_name is not None and len(self.user_name) > 0:
            initial = self._font_icon.render(self.user_name[0], True, self.TEXT_COLOR)
            pane.blit(initial, initial.get_rect(center=(self._icon_center_x, self._icon_center_y)))

            if self._name_alpha  > 0:
                name_surf = self._font_name.render(self.user_name, True, self.TEXT_COLOR)
                name_surf.set_alpha(self._name_alpha)
                name_rect = name_surf.get_rect(center=(self._name_center_x, self._name_center_y))
                pane.blit(name_surf, name_rect)

        surface.blit(pane, (self.pos_x, self.pos_y))

class PasswordInput():
    FIELD_COLOR = (255, 255, 255, 50)
    INPUT_COLOR = (255, 255, 255)

    def __init__(self, width : int, height : int):
        self.password_length = 0
        self.pos_x = 0
        self.pos_y = 0

        self._width = width
        self._height = height
        self._half_height = height // 2
        self._padding = 10
        self._radius = (self._height - (2 * self._padding)) // 4

    def draw(self, surface) -> None:
        field = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        pygame.draw.rect(field, self.FIELD_COLOR, field.get_rect())

        password_width = self._padding + self.password_length * (self._radius * 2 + self._padding)
        is_right_to_left = password_width > self._width

        for n in range(self.password_length):
            diameter = self._radius * 2
            
            center_x = (n + 1) * (self._padding + diameter)
            center_y = self._half_height

            if is_right_to_left:
                center_x = self._width - center_x
            
            pygame.draw.aacircle(field, self.INPUT_COLOR, (center_x, center_y), self._radius)

        surface.blit(field, (self.pos_x, self.pos_y))

class GlassPane():
    BORDER_COLOR = (255, 255, 255, 120)

    def __init__(self, width = 100, height = 100, pos_x = 0, pos_y = 0):
        self.width = width
        self.height = height

        self.pos_x = pos_x
        self.pos_y = pos_y

        self.alpha = 50

        self.border_radius = 20
        self.border_width = 2

    def draw(self, surface : Surface) -> None:
        pane = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        pygame.draw.rect(pane, (255, 255, 255, self.alpha), pane.get_rect(), border_radius=self.border_radius)
        pygame.draw.rect(pane, self.BORDER_COLOR, pane.get_rect(), width=self.border_width, border_radius=self.border_radius)

        surface.blit(pane, (self.pos_x, self.pos_y))

class GamepadLegend:
    FONT_PATH =  Path(__file__).parent / "assets" / "fonts" / "dejavu" / "DejaVuSans-Bold.ttf"
    BUTTON_COLOR = (50, 60, 75)
    PADDING = 10

    def __init__(self, pos_x : int = 0, pos_y : int = 0):
        self.__width = 300
        self.__height = 200

        self.pos_x = pos_x
        self.pos_y = pos_y

        self.__glass_pane = GlassPane(self.__width, self.__height)

        self.__font_digit = pygame.font.Font(self.FONT_PATH, 20)

    def get_width(self) -> int:
        return self.__width

    def get_height(self) -> int:
        return self.__height

    def draw(self, surface : Surface) -> None:
        legend_surface = pygame.Surface((self.__width, self.__height), pygame.SRCALPHA)

        self.__glass_pane.draw(legend_surface)

        trigger_height = 45
        shoulder_width = 35
        shoulder_height = 30

        # Trigger left
        rect = pygame.Rect(self.PADDING, self.PADDING, shoulder_width, trigger_height)
        pygame.draw.rect(legend_surface, self.BUTTON_COLOR, rect, border_radius=6)

        lbl_surf = self.__font_digit.render("8", True, (255, 255, 255))
        legend_surface.blit(lbl_surf, lbl_surf.get_rect(center=(self.PADDING + (shoulder_width // 2), self.PADDING + (trigger_height // 2))))

        # Trigger right
        rect = pygame.Rect(self.__width - self.PADDING - shoulder_width, self.PADDING, shoulder_width, trigger_height)
        pygame.draw.rect(legend_surface, self.BUTTON_COLOR, rect, border_radius=6)

        lbl_surf = self.__font_digit.render("6", True, (255, 255, 255))
        legend_surface.blit(lbl_surf, lbl_surf.get_rect(center=(self.__width - self.PADDING - (shoulder_width // 2), self.PADDING + (trigger_height // 2))))

        # Shoulder left
        rect = pygame.Rect(self.PADDING, self.PADDING + trigger_height + 4, shoulder_width, shoulder_height)
        pygame.draw.rect(legend_surface, self.BUTTON_COLOR, rect, border_radius=6)

        lbl_surf = self.__font_digit.render("7", True, (255, 255, 255))
        legend_surface.blit(lbl_surf, lbl_surf.get_rect(center=(self.PADDING + (shoulder_width // 2), self.PADDING + trigger_height + 4 + shoulder_height // 2)))

        # Shoulder right
        rect = pygame.Rect(self.__width - self.PADDING - shoulder_width, self.PADDING + trigger_height + 4, shoulder_width, shoulder_height)
        pygame.draw.rect(legend_surface, self.BUTTON_COLOR, rect, border_radius=6)

        lbl_surf = self.__font_digit.render("5", True, (255, 255, 255))
        legend_surface.blit(lbl_surf, lbl_surf.get_rect(center=(self.__width - self.PADDING - (shoulder_width // 2), self.PADDING + trigger_height + 4 + shoulder_height // 2)))

        # DPad
        dpad_width = 30
        dpad_x = 20 + self.PADDING
        dpad_y = 75 + self.PADDING


        directions = [
            (0, 1, "1", "0"),
            (1, 0, "2", "9"),
            (2, 1, "3", ""),
            (1, 2, "4", "")
        ]

        for direction in directions:
            dx = direction[0]
            dy = direction[1]
            lbl = direction[2]

            x = dx * (dpad_width + 4) + dpad_x
            y = dy * (dpad_width + 4) + dpad_y

            rect = pygame.Rect(x, y, dpad_width, dpad_width)
            pygame.draw.rect(legend_surface, self.BUTTON_COLOR, rect, border_radius=6)

            lbl_surf = self.__font_digit.render(lbl, True, (255, 255, 255))
            legend_surface.blit(lbl_surf, lbl_surf.get_rect(center=(x + dpad_width // 2, y + dpad_width // 2)))

        # Buttons
        button_radius = 15
        buttons_x = self.__width - 20 - self.PADDING - 6 * button_radius - 8
        buttons_y = 75 + self.PADDING

        for direction in directions:
            dx = direction[0]
            dy = direction[1]
            lbl = direction[3]

            x = dx * (button_radius * 2 + 4) + buttons_x + button_radius
            y = dy * (button_radius * 2 + 4) + buttons_y + button_radius

            pygame.draw.circle(legend_surface, self.BUTTON_COLOR, (x, y), button_radius)

            if lbl != "":
                lbl_surf = self.__font_digit.render(lbl, True, (255, 255, 255))
                legend_surface.blit(lbl_surf, lbl_surf.get_rect(center=(x, y)))

        surface.blit(legend_surface, (self.pos_x, self.pos_y))

class Background():
    def __init__(self):
        pass

    def draw(self, surface : Surface) -> None:
        surface.fill((40, 40, 60))
        
        pygame.draw.circle(surface, (120, 50, 200), (150, 150), 200)
        pygame.draw.circle(surface, (50, 150, 180), (750, 450), 250)
        pygame.draw.circle(surface, (200, 100, 80), (450, 500), 180)