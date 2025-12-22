import os
from engine.core.app import App

main_path = os.path.dirname(os.path.realpath(__file__))


def main():
    app = App(path=main_path)
    app.run()


if __name__ == "__main__":
    main()
