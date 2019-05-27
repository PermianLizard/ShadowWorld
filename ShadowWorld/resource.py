class ResourceCache(object):
    def __init__(self):
        self._cache = {}

    def register(self, name, loader):
        self._cache[name] = loader(name)

    def get(self, name):
        return self._cache[name]


if __name__ == '__main__':
    rc = ResourceCache()


    def load(name):
        return {'name': name}


    rc.register('res1', load)
    rc.register('res2', load)

    print(rc.get('res1'))
    print(rc.get('res2'))
    print(rc.get('res3'))
