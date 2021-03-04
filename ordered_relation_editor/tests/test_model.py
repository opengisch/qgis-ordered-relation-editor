
from qgis.core import QgsVectorLayer, QgsFeature, QgsRelation, QgsProject
from qgis.testing import unittest, start_app

start_app()


class TestImport(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.referenced_layer = QgsVectorLayer("NoGeometry?field=id:integer", "referencedlayer", "memory")
        pr = self.referenced_layer.dataProvider()
        f = QgsFeature()
        f.setFields(self.referenced_layer.fields())
        f.setAttributes([1])
        assert pr.addFeatures([f])
        
        self.referencing_layer = QgsVectorLayer("NoGeometry?field=id:integer&field=foreignkey:integer&field=rank:integer", "referencinglayer", "memory")
        pr = self.referencing_layer.dataProvider()
        features = []
        for i in range(1, 10):
            f = QgsFeature()
            f.setFields(self.referencing_layer.fields())
            f.setAttributes([i, 1, i])
            features.append(f)
        assert pr.addFeatures(features)
        
        rel = QgsRelation()
        rel.setId('rel1')
        rel.setReferencingLayer(self.referencingLayer.id())
        rel.setReferencedLayer(self.referencedLayer.id())
        rel.addFieldPair('foreignkey', 'id')

        assert rel.isValid()

        QgsProject.instance().addMapLayers([self.referencedLayer, self.referencingLayer])
        QgsProject.instance().relationManager().addRelation(rel)

    def tearDown(self):
        QgsProject.instance().removeAllMapLayers()

    def test_move(self):
        pass