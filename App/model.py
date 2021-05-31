﻿"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


from App import config as cf
import math
from DISClib.ADT.graph import gr
from DISClib.ADT import map as mp
from DISClib.ADT import list as lt
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Sorting import mergesort as merge
from DISClib.Utils import error as error
assert cf

# =====================================================
#                       API
# =====================================================


# Construccion de modelos

def newAnalyzer():

    try:
        analyzer = {
                    'cables' : None,
                    'lpVertices' : None,
                    "landingPoints":None,
                    'connections': None,
                    'components': None,
                    'paths' : None
                    }

        analyzer['cables'] = mp.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['lpVertices'] = mp.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)
                                     
        analyzer["landingPoints"] = mp.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=False,
                                              size=14000,
                                              comparefunction=compareLandingPointIds)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# Funciones para agregar informacion al grafo

def addConnections(analyzer, cable):
    """
    Adiciona los landing points al grafo como vertices y arcos entre los landing points adyacentes.

    Los vertices tienen por nombre el identificador del landing point
    seguido del cable que sirve.
    """
    
    origin = formatVertexOrigin(cable)
    destination = formatVertexDestination(cable)
    
    distance = formatDistance(cable, analyzer)
    
    addVertex(analyzer, origin)
    addVertex(analyzer, destination)
    addConnection(analyzer, origin, destination, distance)

    addCable(analyzer,cable)

    addLpVertices(analyzer, cable, "origin", origin)
    addLpVertices(analyzer, cable, "destination", destination)

    addLpConnections(analyzer)
    
    return analyzer
    

# Funciones para agregar informacion a una tabla de hash

def addLP(analyzer, point):
    mp.put(analyzer["landingPoints"],point["landing_point_id"], point)
    return analyzer

def addCable(analyzer,cable):
    existsCable = mp.get(analyzer["cables"], cable["cable_id"])
    if existsCable == None:
        mp.put(analyzer["cables"], cable["cable_id"], cable["capacityTBPS"])
    

# ==============================
# Funciones de consulta
# ==============================

def totalVertices(analyzer):
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    return gr.numEdges(analyzer['connections'])

# ==============================
# Funciones Helper
# ==============================

def formatVertexOrigin(cable):
    name = str(cable['origin']) + '-'
    name = name + str(cable['cable_id'])
    return name

def formatVertexDestination(cable):
    name = str(cable["destination"]) + '-'
    name = name + str(cable["cable_id"])
    return name

def formatDistance(cable, analyzer):
    origin = cable["origin"]
    destination = cable["destination"]
    coordinatesOrigin = getCoordinates(analyzer, origin)
    coordinatesDestination = getCoordinates(analyzer,destination)
    distance = haversine(coordinatesOrigin[0], coordinatesOrigin[1], coordinatesDestination[0], coordinatesDestination[1])
    return distance


def getCoordinates(analyzer, place):
    latitudePlace = mp.get(analyzer["landingPoints"], place)
    latitudePlace = me.getValue(latitudePlace)
    latitudePlace = float(latitudePlace["latitude"])

    longitudePlace = mp.get(analyzer["landingPoints"], place)
    longitudePlace = me.getValue(longitudePlace)
    longitudePlace = float(longitudePlace["longitude"])
    return latitudePlace, longitudePlace

def haversine(lat1, lon1, lat2, lon2):
    # distance between latitudes
    # and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
 
    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0
 
    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) +
         pow(math.sin(dLon / 2), 2) *
             math.cos(lat1) * math.cos(lat2))
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return rad * c 
    # This code is contributed
    # by ChitraNayal

def addVertex(analyzer, vertexid):
    if not gr.containsVertex(analyzer['connections'], vertexid):
        gr.insertVertex(analyzer['connections'], vertexid)
    return analyzer

def addConnection(analyzer, origin, destination, distance):
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, distance)
    return analyzer

def addLpVertices(analyzer, cable, type, vertex):
    existsEntry = mp.get(analyzer["lpVertices"], cable[type])
    if existsEntry == None:
        dataentry = lt.newList('ARRAY_LIST', compareLandingPointIds)
        mp.put(analyzer["lpVertices"],cable[type], dataentry)
    else:
        dataentry = me.getValue(existsEntry)
    lt.addLast(dataentry, vertex)

def addLpConnections(analyzer):
    distance = 0.1
    LpList = mp.keySet(analyzer["lpVerices"])
    for Lp in lt.iterator(LpList):
        vertexList = me.getValue(mp.get(Lp))
        for vertexOrigin in lt.iterator(vertexList):
            for vertexDestination in lt.iterator(vertexList):
                if gr.getEdge(analyzer["connections"], vertexOrigin, vertexDestination) == None and vertexOrigin != vertexDestination:
                    addConnection(analyzer, vertexOrigin, vertexDestination, distance)
    

# ==============================
# Funciones de Comparacion
# ==============================

def compareLandingPointIds(stop, keyValueLP):
    """
    Compara dos estaciones
    """
    LPId = keyValueLP['key']
    if (stop == LPId):
        return 0
    elif (stop > LPId):
        return 1
    else:
        return -1