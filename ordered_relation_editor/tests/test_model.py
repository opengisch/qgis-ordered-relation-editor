
from PyQt5.QtCore import QModelIndex
from qgis.core import QgsVectorLayer, QgsFeature, QgsRelation, QgsProject, QgsFeatureRequest
from qgis.testing import unittest, start_app
from ordered_relation_editor.core.ordered_relation_model import OrderedRelationModel

start_app()


class TestImport(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.referenced_layer = QgsVectorLayer("NoGeometry?field=id:integer", "referencedlayer", "memory")
        pr = self.referenced_layer.dataProvider()
        f0 = QgsFeature()
        f0.setFields(self.referenced_layer.fields())
        f0.setAttributes([1])
        assert pr.addFeatures([f0])
        
        self.referencing_layer = QgsVectorLayer("NoGeometry?field=id:integer&field=foreignkey:integer&field=rank:integer", "referencinglayer", "memory")
        pr = self.referencing_layer.dataProvider()
        features = []
        for i in range(1, 10):
            f = QgsFeature()
            f.setFields(self.referencing_layer.fields())
            f.setAttributes([i, 1, i])
            features.append(f)
        assert pr.addFeatures(features)
        
        relation = QgsRelation()
        relation.setId('rel1')
        relation.setReferencingLayer(self.referencingLayer.id())
        relation.setReferencedLayer(self.referencedLayer.id())
        relation.addFieldPair('foreignkey', 'id')

        assert relation.isValid()

        QgsProject.instance().addMapLayers([self.referencedLayer, self.referencingLayer])
        QgsProject.instance().relationManager().addRelation(relation)

        req = QgsFeatureRequest(1)
        feature = next(self.referenced_layer.getFeatures(req))

        self.model = OrderedRelationModel()
        self.model.init(relation, 'rank', feature, "\"id\"")

    def tearDown(self):
        QgsProject.instance().removeAllMapLayers()

    def features_in_order(self):
        features = []
        for i in range(1, 10):
            idx = self.model.index(i, 0, QModelIndex())
            features.append(self.model.data(idx, OrderedRelationModel.ImagePathRole))
        return features

    def test_move(self):
        self.assertEqual(self.features_in_order(), [i for i in range(1, 10)])
        self.model.moveitems(2, 5)
        self.assertEqual(self.features_in_order(), [1, 2, 4, 5, 2, 6, 7, 8, 9])
