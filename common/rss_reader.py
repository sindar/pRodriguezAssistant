import feedparser

class RSSReader:
    def __init__(self):
        self.current_entry = 0
    def read_entry(self):
        news_feed = feedparser.parse("http://feeds.bbci.co.uk/news/science_and_environment/rss.xml")
        count = len(news_feed.entries)
        if self.current_entry <= count:
            entry = news_feed.entries[self.current_entry]
            self.current_entry += 1
            return str(entry.title) + '. ' + str(entry.summary_detail['value'])
        else:
            return None