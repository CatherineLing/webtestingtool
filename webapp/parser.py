'''
Created on Oct 6, 2012

@author: lingxingjian
'''
from HTMLParser import HTMLParser


class WrongInputException(Exception):
    def __init__(self, pos):
        self.pos = pos
    def __str__(self):
        return "Wrong input at Line %d"%self.pos[0]
    
class State:
    def __init__(self, handlers = None):
        if handlers == None:
            handlers = {}
        self.handlers = handlers
    def trans_link(self, event):
        raise WrongInputException(event.pos)
    def trans_tr_start(self, event):
        raise WrongInputException(event.pos)
    def trans_tr_end(self, event):
        raise WrongInputException(event.pos)
    def trans_td_start(self, event):
        raise WrongInputException(event.pos)
    def trans_td_end(self, event):
        raise WrongInputException(event.pos)
    def trans_table_start(self, event):
        raise WrongInputException(event.pos)
    def trans_table_end(self, event):
        raise WrongInputException(event.pos)
    def trans_data(self, event):
        raise WrongInputException(event.pos)

class StartState(State):
    def trans_link(self, event):
        self.handlers['add_url'](event.data)
        return LinkState(self.handlers)

class LinkState(State):
    def trans_table_start(self, event):
        return TableState(self.handlers)
    
class TableState(State):
    def trans_tr_start(self, event):
        self.handlers['add_row']()
        return TrState(self.handlers)
    def trans_table_end(self, event):
        return EndState(self.handlers)
    
class TrState(State):
    def trans_td_start(self, event):
        return TdState(self.handlers)
    def trans_tr_end(self, event):
        return TableState(self.handlers)
    
class TdState(State):
    def trans_data(self, event):
        self.handlers['add_value'](event.data)
        return DataState(self.handlers)
    def trans_td_end(self, event):
        self.handlers['add_value']('')
        return TrState(self.handlers)
    
class DataState(State):
    def trans_td_end(self, event):
        return TrState(self.handlers)
    
class EndState(State):
    pass

class Event:
    def __init__(self, tag, data, pos):
        self.tag = tag
        self.data = data
        self.pos = pos
        
# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        handlers = {'add_url':self.add_url, 'add_row':self.add_row, 'add_value':self.add_value}
        self.state = StartState(handlers)
        self.url = None
        self.data = []
        
    def add_url(self, value):
        self.url = value
        
    def add_row(self):
        self.data.append([])
        
    def add_value(self, value):
        self.data[-1].append(value)
    
    def handle_starttag(self, tag, attrs):
        if tag == "link":
            self.state = self.state.trans_link(Event(tag, dict(attrs)['href'], self.getpos()))
        elif tag == "table":
            self.state = self.state.trans_table_start(Event(tag, None, self.getpos()))
        elif tag == "tr":
            self.state = self.state.trans_tr_start(Event(tag, None, self.getpos()))
        elif tag == "td":
            self.state = self.state.trans_td_start(Event(tag, None, self.getpos()))
            
        
    def handle_endtag(self, tag):
        if tag == "table":
            self.state = self.state.trans_table_end(Event(tag, None, self.getpos()))
        elif tag == "tr":
            self.state = self.state.trans_tr_end(Event(tag, None, self.getpos()))
        elif tag == "td":
            self.state = self.state.trans_td_end(Event(tag, None, self.getpos()))
            
    def handle_data(self, data):
        if isinstance(self.state, TdState):#ignore any data outside <td>...</td>
            self.state = self.state.trans_data(Event(None, data, self.getpos()))

def parse(htmlscript):
    # instantiate the parser and fed it some HTML
    parser = MyHTMLParser()
    parser.feed(htmlscript)
    data = [row for row in parser.data if len(row) == 3]
    return parser.url, data

def main():
    htmlscript = open('/home/ling/Desktop/celery').read()
    print parse(htmlscript)

if __name__ == '__main__':
    main()