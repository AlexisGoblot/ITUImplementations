from .base_classes import ITU, Model


class ITU2402(ITU):

    def __init__(self):
        name = "A method to predict the statistics of clutter loss for earth-space and aeronautical paths"
        ITU_number = 2402
        tags = ["clutter loss", "earth-space paths", "statistics"]
        ITU.__init__(self, name, ITU_number, tags)

    def model(self):
        pass


if __name__ == "__main__":
    from doctest import testmod

    testmod(verbose=True)
