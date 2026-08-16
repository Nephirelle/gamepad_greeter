import argparse

from service import GreetdAuthenticationService, AuthenticationService, UserService
from game import LoginGame, GameController

def compose_game(is_test : bool) -> LoginGame:
    auth_service = AuthenticationService() if is_test else GreetdAuthenticationService()
    auth_service.init()

    usr_service = None
    if is_test:
        users = ["Bruno", "Hildegart", "Anne", "Bob", "Alice", "Frank"]
        usr_service = UserService(users)
    else:
        usr_service = UserService()

    usr_service.get_users() # Make sure to fail early in case we cannot fetch users

    game_ctrl = GameController(auth_service, usr_service)

    return LoginGame(game_ctrl)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true", help="Test this greeter's UI w/o connecting to daemon")
    args = parser.parse_args()

    game = compose_game(args.test)
    game.init()
    game.run()

if __name__ == '__main__':
    main()