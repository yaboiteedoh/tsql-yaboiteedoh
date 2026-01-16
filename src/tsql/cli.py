import os

from .classes import App
from .templater import Templater

def main():
    templater = Templater(os.getcwd())
    app = App(os.getcwd())
    app.enter()

