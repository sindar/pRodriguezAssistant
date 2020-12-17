import feedparser

class RSSReader:
    def __init__(self, feeds_file, eyes_bl = None):
        self.eyes_bl = eyes_bl
        self.reset(feeds_file)

    def read_feeds(self):
        feeds_list = []
        with open(self.feeds_file,'r') as fin:
            lines = fin.readlines()
        for line in lines:
            record = line.split(';')
            # sentence = line.rstrip('\n\r')
            feeds_list.append(record)
        return feeds_list

    def reset(self, feeds_file = None):
        self.current_entry = 0
        self.entries_count = 0
        self.current_feed_index = 0
        self.current_news_feed = None

        if feeds_file:
            self.feeds_file = feeds_file
            self.feeds_list = self.read_feeds()
            self.feeds_count = len(self.feeds_list)

    def next_feed(self):
        if self.current_feed_index < self.feeds_count:
            self.current_feed_index += 1
            self.current_entry = 0
            self.current_news_feed = feedparser.parse(self.feeds_list[self.current_feed_index][1])
            self.entries_count = len(self.current_news_feed.entries)
        else:
            self.reset()
        return self.read_entry()

    def read_entry(self):
        result = 'RSS feeds list is empty!'
        if self.feeds_count > 0:
            bl_proc = None
            if self.eyes_bl:
                bl_proc = self.eyes_bl.exec_cmd('BLINK_NORMAL')

            if self.current_news_feed == None:
                self.current_news_feed = feedparser.parse(self.feeds_list[self.current_feed_index][1])
                self.entries_count = len(self.current_news_feed.entries)

            result = None
            if self.current_entry <= self.entries_count:
                entry = self.current_news_feed.entries[self.current_entry]
                self.current_entry += 1
                result = str(entry.title) + '. ' + str(entry.summary_detail['value'])

            if bl_proc:
                bl_proc.terminate()
                self.eyes_bl.exec_cmd('ON')

        return result