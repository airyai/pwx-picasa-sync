# -*- encoding: utf-8 -*-

import os, pickle

class HashDB:
    
    def _load_db(self):
        if not os.path.isfile(self.path):
            self._data = {}
            return 
        with open(self.path, 'r') as f:
            new_data = pickle.load(f)
            if not isinstance(new_data, dict):
                raise ValueError(u'File %s is not a valid album database.'
                                 % self.path)
            self._data = new_data
            
    def _save_db(self):
        with open(self.path, 'w') as f:
            pickle.dump(self._data, f)
    
    def __init__(self, path):
        '''
        创建一个 LocalRepo 对象的实例。
        
        参数：
        
        path - 数据库文件的路径。
        '''
        self.path = path
        self._data = {}
        self._load_db()
        
    def load(self):
        '''
        重新从文件读取数据库的内容。
        '''
        self._load_db()
        
    def save(self):
        '''
        将数据库的内容存入文件。
        '''
        self._save_db()
        
    def get(self, key, default_value = None):
        if isinstance(key, tuple) or isinstance(key, list):
            key = u':'.join(key)
        return self._data.get(key, default_value)
    
    def put(self, key, value):
        if isinstance(key, tuple) or isinstance(key, list):
            key = u':'.join(key)
        self._data[key] = value
        
