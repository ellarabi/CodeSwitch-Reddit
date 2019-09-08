class Post:
    """
    A class for posts

    """

    def __init__(self, author, sub_reddit, date, country, confidence, text, lang1, lang2, id, link_id, parent_id):
        """

        :param author: str
            Reddit userid
        :param sub_reddit: str
            subreddit of post
        :param date: int
            Date of the post in unix time
        :param country: str
            country of post, same as the subreddit
        :param confidence: int
            confidence of lang1 given by polyglot

        :param text: str
            the post body
        :param lang1: str
            primary language of the post
        :param lang2: str
            secondary language of post
        :param id: str
            post id given by reddit
        :param link_id: str
            id of the whole Post
        :param parent_id: str
            if the post is a reply, then this is the parent id(post replied to)
        """

        self.author = author
        self.sub_reddit = sub_reddit
        self.text = text
        self.lang1 = lang1
        self.lang2 = lang2
        self.date = date
        self.country = country
        self.confidence = confidence
        self.id = id
        self.link_id = link_id
        self.parent_id = parent_id

    def to_tuple(self):
        return (self.author, self.sub_reddit, self.country, self.date, self.confidence, self.lang1,
                self.lang2, self.text, self.id, self.link_id, self.parent_id)

    @classmethod
    def header(cls):
        return (
            'Author', "Subreddit", "Country", "Date", "confidence", "Lang1", "Lang2", "Text", "id", "link_id",
            "parent_id")
