# -*- encoding: utf-8 -*-

import sys
import threading

import traceback

_status = None

# 字符编码转换
def uni(s):
    if isinstance(s, unicode):
        return s
    return unicode(s, 'utf-8')

def fsuni(s):
    if isinstance(s, unicode):
        return s
    return unicode(s, sys.getfilesystemencoding())


# 取得可阅读的大小说明
def human_size(size):
    if size is None:
        return u'0'
    if size > 1024 * 1024:
        return u'%s M' % round(float(size) / 1024 / 1024, 2)
    if size > 1024:
        return u'%s K' % round(float(size) / 1024, 2)
    return u'%s B' % size

_console_lock = threading.Lock()

def info(msg):
    _console_lock.acquire_lock()
    try:
        sys.stdout.write(uni(msg))
    except UnicodeError:
        sys.stdout.write(u'[**** Unicode Error ****]')
    sys.stdout.write(u'\n')
    _console_lock.release_lock()
    
def err(msg):
    _console_lock.acquire_lock()
    try:
        sys.stderr.write(uni(msg))
    except UnicodeError:
        sys.stderr.write(u'[**** Unicode Error ****]')
    sys.stderr.write(u'\n')
    traceback.print_exc()
    _console_lock.release_lock()

def config_fail(msg):
    err(u'%s' % msg)
    sys.exit(1)
    
def bad_auth(msg):
    err(u'%s' % msg)
    sys.exit(2)
    
def invalid_feed(feed):
    feed = feed[0] if isinstance(feed, tuple) or isinstance(feed, list) else feed
    feed = uni(feed)
    err(u'! 无效的 Feed <%s>' % feed)
    
def feed_load_error(feed):
    feed = feed[0] if isinstance(feed, tuple) or isinstance(feed, list) else feed
    feed = uni(feed)
    err(u'! 无法读取 Feed <%s>。请检查您的网络是否畅通。' % feed)
    
def feed_filter_invalid(feed):
    feed = [uni(s) for s in feed]
    err(u'! Feed <%s> 的过滤器 %s 是无效的正则表达式。' % (feed[0], feed[1]))
    
def album_not_auth(repo):
    err(u'>! 您没有访问相册 <ID=%s> 的权限。' % repo.albumid)

def album_load_error(repo):
    err(u'>! 读取相册 <ID=%s> 的网络数据失败。请确认您的网络是否通畅？' % repo.albumid)
    
def album_db_invalid(repo):
    err(u'>! 相册 <%s> 的数据库已损坏。' % repo.path)
    
def album_db_ioerror(repo):
    err(u'>! 无法打开相册 <%s> 的数据库。' % repo.path)
    
def album_begin(repo):
    info(u'>> 取得相册 <%s> 目录 (%s)。' % (repo.path, len(repo.photos)))
    
def photo_skip(repo, photo, prog_id):
    #info(u'* (%s/%s) 跳过已存在的本地图片 %s/%s。' %
    #                 (prog_id, repo.count, repo.path, photo[0]))
    pass

total_photo_count = 0
total_photo_size = 0

def photo_ok(repo, photo, prog_id):
    global total_photo_count, total_photo_size
    total_photo_count += 1
    total_photo_size += photo[3]
    info(u'+ (%s/%s) 新增图片 %s/%s (%s)。' %
            (prog_id, repo.count, repo.path, photo[0], human_size(photo[3]))
        )
    

def photo_load_error(repo, photo, prog_id):
    err(u'! (%s/%s) 下载图片 %s/%s 失败。请确认您的网络是否通畅？' %
                     (prog_id, repo.count, repo.path, photo[0]))
    
def photo_zero_error(repo, photo, prog_id):
    err(u'! (%s/%s) 下载图片 %s/%s 失败。文件内容为空？' %
                     (prog_id, repo.count, repo.path, photo[0]))
    
def photo_io_error(repo, photo, prog_id):
    err(u'! (%s/%s) 存储图片至 %s/%s 失败。磁盘是否无法写入？' %
                     (prog_id, repo.count, repo.path, photo[2]))
    
def all_finished():
    info(u'\n全部完成，本次共更新 %s 张图片，总计 %s。' % 
            (total_photo_count, human_size(total_photo_size)) )
    
