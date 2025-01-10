from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsProject,
    QgsRelation,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QModelIndex
from qgis.testing import start_app, unittest

from ordered_relation_editor.core.ordered_relation_model import OrderedRelationModel

start_app()


class TestModel(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.referenced_layer = QgsVectorLayer(
            "NoGeometry?field=id:integer", "referencedlayer", "memory"
        )
        pr = self.referenced_layer.dataProvider()
        f0 = QgsFeature()
        f0.setFields(self.referenced_layer.fields())
        f0.setAttributes([1])
        assert pr.addFeatures([f0])

        self.referencing_layer = QgsVectorLayer(
            "NoGeometry?field=id:integer&field=foreignkey:integer&field=rank:integer",
            "referencinglayer",
            "memory",
        )
        pr = self.referencing_layer.dataProvider()
        features = []
        for i in range(0, 10):
            f = QgsFeature()
            f.setFields(self.referencing_layer.fields())
            f.setAttributes([i + 1, 1, i + 1])
            features.append(f)
        assert pr.addFeatures(features)

        QgsProject.instance().addMapLayers(
            [self.referenced_layer, self.referencing_layer]
        )

        self.relation = QgsRelation()
        self.relation.setName("rel1")
        self.relation.setId("rel1")
        self.relation.setReferencingLayer(self.referencing_layer.id())
        self.relation.setReferencedLayer(self.referenced_layer.id())
        self.relation.addFieldPair("foreignkey", "id")

        assert self.relation.isValid()

        QgsProject.instance().relationManager().addRelation(self.relation)

        req = QgsFeatureRequest(1)
        feature = next(self.referenced_layer.getFeatures(req))

        self.model = OrderedRelationModel()
        self.model.init(self.relation, "rank", feature, '"id"', "")

    def tearDown(self):
        QgsProject.instance().removeAllMapLayers()

    def test_order(self):
        self.assertEqual(self.__features_in_order(), [i + 1 for i in range(0, 10)])

    def test_move(self):
        self.assertEqual(self.__features_in_order(), [i + 1 for i in range(0, 10)])
        self.model.moveitems(2, 5)
        self.assertEqual(self.__features_in_order(), [1, 2, 4, 5, 6, 3, 7, 8, 9, 10])

    def __features_in_order(self):
        features = []
        for r in range(0, 10):
            idx = self.model.index(r, 0, QModelIndex())
            features.append(self.model.data(idx, OrderedRelationModel.ImagePathRole))
        return features
