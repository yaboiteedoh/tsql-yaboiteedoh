import os

from classes import App

def main():
    app = App(os.getcwd())
    app.enter()

if __name__ == '__main__':
    main()
    
