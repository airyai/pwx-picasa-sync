# -*- encoding: utf-8 -*-

import gdata.photos.service
import urllib2

class GClient:
    CLIENT_NAME = 'net.ipwx.robot.picasa-sync'
    
    def __init__(self, username, password):
        '''
        初始化 GClient 实例。
        
        参数：
        
        username -- 用户登陆邮箱。
        password -- 用户登陆密码。如果是二次登陆，请使用 AppPassword。
        '''
        # TODO: catch gdata.service.BadAuthentication
        #       and gdata.service.Error
        #       and gdata.service.NotAuthenticated
        photo = self.photo = gdata.photos.service.PhotosService()
        
        if username is not None and password is not None:
            photo.email = username
            photo.password = password
            photo.source = GClient.CLIENT_NAME
            photo.ProgrammaticLogin()
    
    def __get_real_photo_url(self, url):
        return '/s0/'.join(url.rsplit('/', 1))
    
    def Clone(self):
        gd = GClient(None, None)
        if self.photo.email is not None:
            gd.photo.email = self.photo.email
            gd.photo.password = self.photo.password
            gd.photo.source = self.photo.source
            gd.photo.SetClientLoginToken(self.photo.GetClientLoginToken())
        return gd
        
            
    def GetPhotos(self, userid, albumid):
        '''
        取得给定用户、给定相册的图片列表。
        
        返回值：
        
        {
            'title': album title,
            'photos': [ photo ]
        }
        '''
        photos = self.photo.GetFeed(u'/data/feed/api/user/%s/albumid/%s?kind=photo'
                                    % (userid, albumid))
        return {
                'title'     : photos.title.text,
                'name'      : photos.name.text,     # NOTE: picasa use this as perm-link
                'user'      : photos.nickname.text,
                'photos'    :
                [[
                    photo.title.text,
                    self.__get_real_photo_url(photo.content.src),
                    None, None
                ] for photo in photos.entry]
            }
        
    def DownPhoto(self, url, target):
        '''
        下载给定 URL 的图片到本地路径。
        '''
        pic = None
        cnt = None
        
        try:
            pic = urllib2.urlopen(url)
            cnt = pic.read()
        except urllib2.URLError:
            if pic is not None:
                pic.close()
            raise
        
        if len(cnt) == 0:
            raise ValueError('Zero content file.')
        
        with open(target, 'wb') as f:
            f.write(cnt)
            f.close()
            
        return len(cnt)
        
