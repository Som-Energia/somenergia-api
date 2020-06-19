from yamlns import namespace as ns
import os.path


class LocalGroups(object):
    def __init__(self, dump):
        self.geolevel = 'lg'
        self.data = dump

    def aliasFilters(self, code):
        lg = self.data.get(code, None)
        if not lg:
            return None
        return [(lg.geolevel, code) for code in lg.codes]

    def getLocalGroups(self):
        return [(k, lg.name) for k, lg in self.data.items()]

#TODO: obtenir la llista de (level, codi) de filtres que el conformen
#TODO: quan tinguem el resultat del aggregate () -> sumar i canviar el nom del
#TODO: llista de grups locals: codi: nom


def loadYamlLocalGroups(relativeFile='../data/alias/gl.yaml'):
    myPath = os.path.abspath(os.path.dirname(__file__))
    dataFile = os.path.join(myPath, relativeFile)
    content = ns.load(dataFile)
    return LocalGroups(content)