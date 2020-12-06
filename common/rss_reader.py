import feedparser

class RSSReader:
    def __init__(self, eyes_bl = None):
        self.current_entry = 0
        self.eyes_bl = eyes_bl

    def read_entry(self):
        bl_proc = None        
        if self.eyes_bl:
            bl_proc = self.eyes_bl.exec_cmd('BLINK_NORMAL')

        result = None
        news_feed = feedparser.parse("http://feeds.bbci.co.uk/news/science_and_environment/rss.xml")
        count = len(news_feed.entries)
        if self.current_entry <= count:
            entry = news_feed.entries[self.current_entry]
            self.current_entry += 1
            result = str(entry.title) + '. ' + str(entry.summary_detail['value'])
        if bl_proc:
            bl_proc.terminate()
            self.eyes_bl.exec_cmd('ON')

        return result