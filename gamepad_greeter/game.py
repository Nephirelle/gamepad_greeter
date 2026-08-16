import sys
import pygame
import traceback

from ui import Background
from service import AuthenticationService, UserService
from view import GameView, UserView, PasswordView
from pygame import Surface
from pygame.event import Event
from pygame.joystick import Joystick

class GameController:
    def __init__(self, auth_service : AuthenticationService, user_service : UserService):
        self._auth_service = auth_service
        self._user_service = user_service
        
        self._joysticks : dict[int, Joystick] = {} # Joysticks by instance ID

        users = self._user_service.get_users()

        self.__user_view = UserView(users)
        self.__user_view.confirmation_callable = self.__on_user_confirmed

        self.__password_view = PasswordView()
        self.__password_view.confirmation_callable = self.__on_password_entered
        self.__password_view.exit_callable = self.__on_return_to_user_selection

        self.__current_view : GameView = self.__user_view

        self._selected_user : str = None

        self._is_running = True

    def init(self) -> None:
        self.__user_view.init()
        self.__password_view.init()

    def is_running(self) -> bool:
        return self._is_running

    def handle_events(self, events : list[Event]) -> None:
        for evt in events:
            self.__handle_if_quit_event(evt)

            if self._is_running:
                self.__handle_if_joydevice_changed_event(evt)
                self.__current_view.handle_event(evt)

    def update(self, surface_width : int, surface_height : int) -> None:
        self.__current_view.update(surface_width, surface_height)

    def draw(self, surface : Surface) -> None:
        self.__current_view.draw(surface)

    def __handle_if_quit_event(self, event : Event) -> None:
        if event.type == pygame.QUIT:
            self._is_running = False

    def __handle_if_joydevice_changed_event(self, event : Event) -> None:
        if event.type == pygame.JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)

            instance_id = joystick.get_instance_id()
            self._joysticks[instance_id] = joystick

        elif event.type == pygame.JOYDEVICEREMOVED:
            self._joysticks.pop(event.instance_id, None)

    def __on_user_confirmed(self, usr : str) -> None:
        try:
            if self._selected_user is not None:
                # Session for selected user already running
                if self._selected_user == usr:
                    self.__current_view = self.__password_view
                    return

                # Session for another user running:
                # Cancel the previous session
                else:
                    self._auth_service.cancel_session()

            # New user was selected: Create session
            self._auth_service.create_session(usr)
            self._selected_user = usr
            self.__password_view.user_name = usr
            self.__current_view = self.__password_view
        except Exception:
            print(traceback.format_exc())

    def __on_password_entered(self, passwd : str) -> bool:
        try:
            self._auth_service.send_password(passwd)
            self._auth_service.start_session(["startxfce4"], [])
        except Exception:
            return False
        
        self._is_running = False

        return True

    def __on_return_to_user_selection(self) -> None:
        self.__current_view = self.__user_view

class LoginGame():
    def __init__(self, controller : GameController):
        self.__controller = controller

    def init(self) -> None:
        pygame.init()
        pygame.font.init()
        
        self.__background = Background()
        self.__controller.init()

    def run(self) -> None:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        clock = pygame.time.Clock()

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        try:
            while self.__controller.is_running():
                events = pygame.event.get()
                
                self.__controller.handle_events(events)

                if not self.__controller.is_running():
                    return
                
                self.__controller.update(screen_width, screen_height)
                self.__background.draw(screen)
                self.__controller.draw(screen)

                pygame.display.flip()
                clock.tick(60)
        except Exception:
            print(traceback.format_exc())
        finally:
            pygame.quit()
            sys.exit()