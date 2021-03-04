# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from enum import Enum
from qgis.PyQt.QtCore import pyqtSlot, pyqtSignal, pyqtProperty, Qt, QObject, QAbstractTableModel, QModelIndex
from qgis.core import QgsRelation, QgsFeature, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, QgsMessageLog

Debug = True


class Role(Enum):
    RelationRole = Qt.UserRole + 1
    RelationIdRole = Qt.UserRole + 2
    AggregateRole = Qt.UserRole + 3
    FieldRole = Qt.UserRole + 4


class OrderedRelationModel(QAbstractTableModel):

    ImagePathRole = Qt.UserRole + 1
    DesriptionRole = Qt.UserRole + 2

    signal = pyqtSignal()

    def __init__(self, parent: QObject = None):
        super(OrderedRelationModel, self).__init__(parent)
        self._relation = QgsRelation()
        self._ordering_field = str()
        self._image_path = str()
        self._description = str()
        self._feature = QgsFeature()
        self._related_features = []

    def init(self, relation: QgsRelation, ordering_field: str, feature: QgsFeature, image_path: str, description: str):
        self._relation = relation
        self._ordering_field = ordering_field
        self._image_path = image_path
        self._description = description
        self._feature = feature
        self._updateData()

        self._relation.referencingLayer().editingStarted.connect(self.editingStarted)
        self._relation.referencingLayer().editingStopped.connect(self.editingStopped)

        self.layerEditingEnabled = self._relation.referencingLayer().isEditable()

    @pyqtSlot()
    def editingStarted(self):
        self.layerEditingEnabled = True

    @pyqtSlot()
    def editingStopped(self):
        self.layerEditingEnabled = False

    @pyqtProperty(int, notify=signal)
    def layerEditingEnabled(self):
        return self._layerEditingEnabled

    @layerEditingEnabled.setter
    def layerEditingEnabled(self, value):
        self._layerEditingEnabled = value
        self.signal.emit()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._related_features)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 1

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return flags

    def data(self, index: QModelIndex, role: int = ...):
        if index.row() < 0 or index.row() >= self.rowCount(QModelIndex()):
            return None

        if role == self.ImagePathRole:
            exp = QgsExpression(self._image_path)
            context = QgsExpressionContext()
            context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(self._relation.referencingLayer()))
            context.setFeature(self._related_features[index.row()])
            res = exp.evaluate(context)
            #if Debug:
            #     QgsMessageLog.logMessage(res)
            return res

        if role == self.DesriptionRole:
            exp = QgsExpression(self._description)
            context = QgsExpressionContext()
            context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(self._relation.referencingLayer()))
            context.setFeature(self._related_features[index.row()])
            res = exp.evaluate(context)
            #if Debug:
            #     QgsMessageLog.logMessage(res)
            return res

        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if index.row() < 0 or index.row() >= self.rowCount(QModelIndex()):
            return False

        return False

    @pyqtSlot(int, int)
    def moveitems(self, index_from, index_to):
        print(index_from, index_to)
        if index_from == index_to:
            return

        field_index = self._relation.referencingLayer().fields().indexFromName(self._ordering_field)
        if field_index < 0:
            return

        start_index = min(index_from, index_to)
        end_index = max(index_from, index_to)
        delta = 1 if index_from > index_to else -1

        self.beginResetModel()

        for i in range(start_index, end_index+1):
            f = self._related_features[i]
            if i == index_from:
                self._related_features[i][self._ordering_field] = index_to + 1  # ranks are index +1 (start at 1)
            else:
                self._related_features[i][self._ordering_field] += delta

            res = self._relation.referencingLayer().changeAttributeValue(f.id(), field_index, f[self._ordering_field])
            print(res)

        sorted(self._related_features, key=lambda _f: _f[self._ordering_field])

        self.endResetModel()
        # TODO: why do we need this, shoud be good before
        self._updateData()

    def roleNames(self):
        return {
            self.ImagePathRole: b'ImagePath',
            self.DesriptionRole: b'Description'
        }

    def _updateData(self):
        self.beginResetModel()
        self._related_features = []

        if len(self._ordering_field) > 0 and self._relation.isValid() and self._feature.isValid():
            request = self._relation.getRelatedFeaturesRequest(self._feature)
            for f in self._relation.referencingLayer().getFeatures(request):
                self._related_features.append(f)

            sorted(self._related_features, key=lambda _f: _f[self._ordering_field])

        self.endResetModel()




