# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from qgis.PyQt.QtWidgets import QGridLayout, QLabel
from qgis.gui import QgsAbstractRelationEditorConfigWidget


class OrderedRelationEditorConfigWidget(QgsAbstractRelationEditorConfigWidget):

    def __init__(self, relation, parent):
        super().__init__(relation, parent)
        self.relation = relation
        self.mOrderingFieldComboBox.setLayer(relation.referencingLayer())
        self.mImagePathExpressionWidget.setLayer(relation.referencingLayer())

    def config(self):
        return {
            'ordering_field': self.mOrderingFieldComboBox.currentField(),
            'image_path': self.mImagePathExpressionWidget.currentField()
        }

    def setConfig(self, config):
        self.mOrderingFieldComboBox.setField(config.get('ordering_field'))
        self.mImagePathExpressionWidget.setField(config.get('image_path'))
