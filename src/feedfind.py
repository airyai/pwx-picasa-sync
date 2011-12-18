# -*- encoding: utf-8 -*-

import re

from console import uni

class FeedDiscover:
    def __init__(self):
        pass
    
    _FEED_PATTERN = re.compile(u'([0-9]+)([^0-9]+([0-9]+))?')
    def parse(self, feed):
        '''
        通过 feed 字符串解析其所代表的 userid 和 albumid。
        不会检查 feed 是否合法，只是简单地从中取出 1~2 个数字串。
        若只有一个数字串，则作为 userid，否则依次作为 userid 和
        albumid。
        '''
        mt = FeedDiscover._FEED_PATTERN.search(feed)
        if mt is None:
            return None
        return ( mt.groups()[0], mt.groups()[2] )
    
    def discover(self, feed, gclient, inverse = False):
        '''
        解析 feed 所包含的相册列表。
        
        feed 应该是一个包含 userid 与 (optional) albumid 的
        字符串，或者是一个元组。其中，元组的第二项是用以过滤相册名
        的正则表达式。
        
        返回列表，每个元素是一个包含了 (userid, albumid) 的元组.
        '''
        gclient = gclient.photo
        
        # 检查参数
        m_test = lambda nm: True
        
        if isinstance(feed, list) or isinstance(feed,tuple):
            regex = re.compile(uni(feed[1]))
            m_test = lambda nm: regex.search(nm)
            if len(feed) > 2:
                inverse = not not feed[2]
            feed = feed[0]
            
        feed = uni(feed)
        
        # 解析 feed 来源
        feed = self.parse(feed)
        if feed is None:
            raise ValueError(u'Invalid feed %s.' % feed)
        
        # 如果指定了 albumid，则直接返回
        if feed[1] is not None:
            return ( tuple(feed), )
        
        # 读取所有 Albums
        ret = []
        albums = gclient.GetUserFeed(user=feed[0])
        
        for album in albums.entry:
            title = uni(album.title.text)
            pass_test = m_test(title)
            if inverse: 
                pass_test = not pass_test
            if pass_test:
                mid = uni(album.id.text)
                ret.append( (feed[0], mid[mid.rfind(u'/')+1:]) )
                
        return tuple(ret)
    
