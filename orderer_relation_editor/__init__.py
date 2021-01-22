# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2
#
# -----------------------------------------------------------


def classFactory(iface):
    """Load plugin.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from orderer_relation_editor.core.ordered_relation_editor_plugin import OrderedRelationEditorPlugin
    return OrderedRelationEditorPlugin(iface)
