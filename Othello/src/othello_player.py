class OthelloPlayer(object):
    def __init__(self, color: int, name: str = "Human"):
        self.name = name
        self.color = color

    def get_move(self, manager: 'OthelloGameManager'):
        pass