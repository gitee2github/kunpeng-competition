# Copyright (c) 2016 ChinaC Inc.


class Page(list):
    def __init__(self, l, prev=None, next=None):
        super(Page, self).__init__(l)
        self.prev = prev
        self.next = next
