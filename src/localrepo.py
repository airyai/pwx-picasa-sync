# -*- encoding: utf-8 -*-

import os, time
import itertools

import gdata.service
import gdata.photos.service

from hashdb import HashDB
import console
from console import uni

# 过滤不适合作为路径名称的字符
def filter_fs_name(n):
    evils = set( ur'/\:*?"<>|' )
    return u''.join([
                    ch for ch in n if ch not in evils
                 ])

# 本地 Repository 的实现
class LocalRepo:
    '''
    将目录作为一个 Picasa 相册的本地镜像管理。
    
    程序会完全独占整个目录，并且在这个目录下面创建 .picasaalbum
    文件，用以记录相册的状态。如果目录不存在，将会尝试创建这个目录。
    '''
    
    def __init__(self, basepath, userid, albumid, gclient):
        self.gclient = gclient
        # 记录相册信息
        self.userid = uni(userid)
        self.albumid = uni(albumid)
        # 检查路径是否存在
        self.basepath = uni(basepath)   # 我们假定配置文件一定是 UTF-8
        #self.path = uni(path)           # 我们假定配置文件一定是 UTF-8
        #self.fullpath = os.path.join(self.basepath, self.path)
        
    def do_init(self):
        '''
        本来这些代码是放在 __init__ 里面的，但是在 picasasync.py 里面，
        需要用到这个类的实例来格式化出错信息，于是就单独提出来了……
        
        尽情地吐嘈我的渣设计吧 OTZ ....
        '''
        # 直接拉取相册的所有信息
        ret = self.gclient.GetPhotos(self.userid, self.albumid)
        self.user = uni(ret['user'])
        self.name = uni(ret['name'])
        self.title = uni(ret['title'])
        self.photos = ret['photos']
        self.count = len(self.photos)
        
        # 计算相册路径
        self.path = os.path.join(self.user, filter_fs_name(
                                            u'%s-%s' % (self.name, self.title)
                                ))
        self.fullpath = os.path.join(self.basepath, self.path)
        
        if not os.path.isdir(self.fullpath):
            os.makedirs(self.fullpath, mode=0755)
        
        # 建立数据库对象
        self.db = HashDB(os.path.join(self.fullpath, '.picasaalbum'))
        
    def _get_next_available_filename(self, name):
        if not os.path.exists(os.path.join(self.fullpath, name)):
            return name
        part = os.path.splitext(name)
        for i in itertools.count(1):
            name = (u'.%s' % i).join(part)
            if not os.path.exists(os.path.join(self.fullpath, name)):
                return name
    
    def _callback(self, callback, *args):
        if callback is not None:
            callback(*args)
    
    def sync(self):
        prog_id = 0
        gclient = self.gclient
        
        for photo in self.photos:
            prog_id += 1
            photo[0] = uni(photo[0])    # 注意我们把 picasa 文件名（utf-8）转换为 unicode
                                        # 如若不然，则 Windows 必定会出错！
            
            # 检查文件名是否已经下载
            if self.db.get(['PIC', photo[1]]) is not None:
                console.photo_skip(self, photo, prog_id)
                continue
            fname = self._get_next_available_filename(filter_fs_name(photo[0]))
            photo[2] = uni(fname)
            # 下载文件
            try:
                photo[3] = gclient.DownPhoto(photo[1],
                                             os.path.join(self.fullpath, fname)
                                            )
            except gdata.service.Error:
                console.photo_load_error(self, photo, prog_id)
                continue
            except gdata.photos.service.GooglePhotosException:
                console.photo_load_error(self, photo, prog_id)
                continue
            except IOError:
                console.photo_io_error(self, photo, prog_id)
                continue
            except ValueError:
                console.photo_zero_error(self, photo, prog_id)
                continue
            
            # 存储文件信息
            self.db.put([u'PIC', photo[1]], (time.time(), fname))
            self.db.save()
            console.photo_ok(self, photo, prog_id)
            
        
    
        
