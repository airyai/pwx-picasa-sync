#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys, os, re
import threadpool
import gdata.service
import gdata.photos.service

from localrepo import LocalRepo
from gclient import GClient
from feedfind import FeedDiscover
from configfile import load_config

import console
from console import uni

# 解析命令行参数、选择合适的配置文件
cfg_path = None
if len(sys.argv) < 2:
    path_to_try = [
        os.path.join(os.getcwd(), 'picasasync.conf'),
        os.path.join(os.getcwd(), '.picasasync'),
        os.path.expanduser('~/picasasync.conf'),
        os.path.expanduser('~/.picasasync'),
    ]
    for i in range(0, len(path_to_try)):
        p = path_to_try[i] = os.path.abspath(uni(path_to_try[i]))
        if os.path.isfile(p):
            cfg_path = p
            break
    if cfg_path is None:
        console.config_fail(u'没有指定配置文件，且在以下路径找不到默认配置：\n\n%s'
                            % u'\n'.join(path_to_try))
else:
    cfg_path = os.path.abspath(uni(sys.argv[1]))
    if not os.path.isfile(cfg_path):
        console.config_fail(u'指定的配置文件 %s 并不存在。' % cfg_path)

# 读取配置
try:
    cfg = load_config(cfg_path)
except IOError:
    console.config_fail(u'无法读取配置文件 %s。' % cfg_path)
except SyntaxError:
    console.config_fail(u'配置文件 %s 存在，但是语法不正确。' % cfg_path)
except Exception:
    console.config_fail(u'配置文件 %s 存在，且语法正确，但无法正确执行。' % cfg_path)

if cfg is None or not isinstance(cfg, dict):
    console.config_fail(u'配置文件 %s 已经载入，但是该配置无效。' % cfg_path)

cfg['basepath'] = os.path.abspath(uni(cfg['basepath']))

console.info(u'配置文件 %s 已载入 (Workers=%s)。' % (cfg_path, cfg.get('workers', 20)))
console.info(u'相册根路径：%s。' % cfg['basepath'])

# 状态汇报：回调方法
prog_album_photo_id = 1

# 创建 Google API 客户端并验证身份
try:
    console.info(u'正在连接 Picasa 服务器……')
    clt = GClient(cfg['username'], cfg['password'])
except gdata.service.BadAuthentication:
    console.bad_auth(u'您的账号 <%s> 不能通过验证。' % uni(cfg['username']))
except gdata.service.Error:
    console.bad_auth (u'无法登陆 Google 相册服务。\n\n'
        u'这个程序并不支持代理服务器的设定哦～如果需要通过代理\n'
        u'访问的话，Linux 用户请使用 proxychains，Windows\n'
        u'用户请使用 sockscap 或 tsocks。')
clients = [
    clt.Clone() for i in range(0, cfg.get('workers', 20))
]

#
# VERSION 2.0: 线程池并发请求版
#
# 建立线程池
workers = threadpool.ThreadPool(cfg.get('workers', 20), clients)
fdis = FeedDiscover()

# 第一步：载入所有相册的信息
def load_feed(clt, feed):
    try:
        return fdis.discover(feed, clt)
    except re.error:
        console.feed_filter_invalid(feed)
    except ValueError:
        console.invalid_feed(feed)
    except gdata.service.Error:
        console.feed_load_error(feed)
    except gdata.photos.service.GooglePhotosException:
        console.feed_load_error(feed)

for feed in cfg['feeds']:        
    workers.make_job(load_feed, feed)
workers.wait()

albums = []
for r in workers.jar:
    albums.extend(r)
    
workers.jar = []

# 第二步：下载所有已知相册的图片
def load_album(clt, album):
    # 初始化相册
    repo = None
    try:
        repo = LocalRepo(cfg['basepath'], album[0], album[1], clt)
        repo.do_init()
    except gdata.service.NotAuthenticated:
        console.album_not_auth(repo)
        return
    except gdata.service.Error:
        console.album_load_error(repo)
        return
    except ValueError:
        console.album_db_invalid(repo)
        return
    except IOError:
        console.album_db_ioerror(repo)
        return
    except gdata.photos.service.GooglePhotosException:
        console.album_load_error(repo)
        return
    # 显示相册信息
    console.album_begin(repo)
    # 更新相册
    repo.sync()

for album in albums:        
    workers.make_job(load_album, album)
workers.wait()

console.all_finished()



