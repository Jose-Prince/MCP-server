class Game:
    def __init__(self, name, price, genre, platforms, average_forever, average_2weeks, median_forever, median_2weeks, ccu, genres, tags, score, release_date, recommensations):
        self.name = name
        self.price = price
        self.genre = genre
        self.platforms = platforms
        self.average_forever = average_forever
        self.average_2weeks = average_2weeks
        self.median_forever = median_forever
        self.median_2weeks = median_2weeks
        self.ccu = ccu
        self.genres = genres
        self.tags = tags
        self.release_date = release_date
        self.score = score
        self.recommendations = recommensations
