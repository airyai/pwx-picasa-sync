# -*- encoding: utf-8 -*-

def load_config(path):
    ret = {}
    def commit(cfg):
        ret.update(cfg)
    execfile(path, {}, {'config': commit})
    return ret
