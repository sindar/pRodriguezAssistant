import feedparser

class RSSReader:
    def __init__(self, eyes_bl = None):
        self.current_entry = 0
        self.entries_count = 0
        self.news_feed = None
        self.eyes_bl = eyes_bl
    
    def reset(self):
        self.current_entry = 0
        self.entries_count = 0
        self.news_feed = None

    def read_entry(self):
        bl_proc = None        
        if self.eyes_bl:
            bl_proc = self.eyes_bl.exec_cmd('BLINK_NORMAL')

        if self.news_feed == None:
            self.news_feed = feedparser.parse("http://feeds.bbci.co.uk/news/science_and_environment/rss.xml")
            self.entries_count = len(self.news_feed.entries)

        result = None
        if self.current_entry <= self.entries_count:
            entry = self.news_feed.entries[self.current_entry]
            self.current_entry += 1
            result = str(entry.title) + '. ' + str(entry.summary_detail['value'])

        if bl_proc:
            bl_proc.terminate()
            self.eyes_bl.exec_cmd('ON')

        return result