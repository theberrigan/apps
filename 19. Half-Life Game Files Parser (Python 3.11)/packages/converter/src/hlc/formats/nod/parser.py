from ...common import bfw
from ...common.consts import MAPS_DIR, GRAPHS_DIR
from ...maths import Vec3
from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



# CACHE_ENTRY
class GraphCacheEntry:
    def __init__ (self):
        self.vec              : Vec3 = [ 0, 0, 0 ]
        self.nearestNodeIndex : int  = -1           # Nearest node or -1 if no node found


# CNode (size 88)
class GraphNode:
    SIZE = 88

    def __init__ (self):
        self.origin         = None    # Vector m_vecOrigin      -- location of this node in space
        self.originPeek     = None    # Vector m_vecOriginPeek  -- location of this node (LAND nodes are NODE_HEIGHT higher).
        self.region         = None    # BYTE   m_Region[3]      -- Which of 256 regions do each of the coordinate belong?
        self.nodeInfo       = None    # int    m_afNodeInfo     -- bits that tell us more about this location
        self.linkCount      = None    # int    m_cNumLinks      -- how many links this node has
        self.firstLinkIndex = None    # int    m_iFirstLink     -- index of this node's first link in the link pool.

        # Where to start looking in the compressed routing table (offset into m_pRouteInfo).
        # (4 hull sizes -- smallest to largest + fly/swim), and secondly, door capability.
        self.nextBestNode   = None    # int    m_pNextBestNode[MAX_NODE_HULLS][2]

        # Used in finding the shortest path. m_fClosestSoFar is -1 if not visited.
        # Then it is the distance to the source. If another path uses this node
        # and has a closer distance, then m_iPreviousNode is also updated.
        self.closestSoFar   = None    # float  m_flClosestSoFar -- Used in finding the shortest path.
        self.prevNode       = None    # int    m_iPreviousNode
        self.hintType       = None    # short  m_sHintType      -- there is something interesting in the world at this node's position
        self.hintActivity   = None    # short  m_sHintActivity  -- there is something interesting in the world at this node's position
        self.hintYaw        = None    # float  m_flHintYaw      -- monster on this node should face this yaw to face the hint.


# CLink (size 24)
class GraphLink:
    SIZE = 24

    def __init__ (self):
        self.srcNodeIndex   = None    # int        m_iSrcNode              -- the node that 'owns' this link ( keeps us from having to make reverse lookups )
        self.dstNodeIndex   = None    # int        m_iDestNode             -- the node on the other end of the link.
        self.blockEntity    = None    # entvars_t* m_pLinkEnt              -- the entity that blocks this connection (doors, etc)

        # m_szLinkEntModelname is not necessarily NULL terminated (so we can store it in a more alignment-friendly 4 bytes)
        self.blockModelName = None    # char       m_szLinkEntModelname[4] -- the unique name of the brush model that blocks the connection (this is kept for save/restore)
        self.linkInfo       = None    # int        m_afLinkInfo            -- information about this link
        self.ownNodeIndex   = None    # float      m_flWeight              -- length of the link line segment


# DIST_INFO
class GraphDistInfo:
    SIZE = 16

    def __init__ (self):
        self.sortedBy     = None    # int m_SortedBy[3]
        self.checkedEvent = None    # int m_CheckedEvent


# CGraph (size 8396)
class Graph:
    SIZE = 8396

    def __init__ (self):
        self.filePath             = None
        self.version              = 0
        self.isGraphPresent       = None   # BOOL        m_fGraphPresent      -- is the graph in memory?
        self.isGraphPtrsSet       = None   # BOOL        m_fGraphPointersSet  -- are the entity pointers for the graph all set?
        self.isRoutingComplete    = None   # BOOL        m_fRoutingComplete   -- are the optimal routes computed, yet?
        self.nodes                = None   # CNode*      m_pNodes             -- pointer to the memory block that contains all node info
        self.links                = None   # CLink*      m_pLinkPool          -- big list of all node connections
        self.routeInfos           = None   # char*       m_pRouteInfo         -- compressed routing information the nodes use.
        self.nodeCount            = None   # int         m_cNodes             -- total number of nodes
        self.linkCount            = None   # int         m_cLinks             -- total number of links
        self.routeInfoSize        = None   # int         m_nRouteInfo         -- size of m_pRouteInfo in bytes.

        # Tables for making the nearest node lookup faster. SortedBy provided nodes in an
        # order of a particular coordinate. Instead of doing a binary search, RangeStart
        # and RangeEnd let you get to the part of SortedBy that you are interested in.
        # Once you have a point of interest, the only way you'll find a closer point is
        # if at least one of the coordinates is closer than the ones you have now. So we
        # search each range. After the search is exhausted, we know we have the closest node
        self.distInfos            = None    # DIST_INFO*  m_di                 -- This is m_cNodes long, but the entries don't correspond to CNode entries.
        self.rangeStart           = None    # int         m_RangeStart[3][256]
        self.rangeEnd             = None    # int         m_RangeEnd[3][256]
        self.shortest             = None    # float       m_flShortest
        self.nearest              = None    # int         m_iNearest
        self.minX                 = None    # int         m_minX
        self.minY                 = None    # int         m_minY
        self.minZ                 = None    # int         m_minZ
        self.maxX                 = None    # int         m_maxX
        self.maxY                 = None    # int         m_maxY
        self.maxZ                 = None    # int         m_maxZ
        self.minBoxX              = None    # int         m_minBoxX
        self.minBoxY              = None    # int         m_minBoxY
        self.minBoxZ              = None    # int         m_minBoxZ
        self.maxBoxX              = None    # int         m_maxBoxX
        self.maxBoxY              = None    # int         m_maxBoxY
        self.maxBoxZ              = None    # int         m_maxBoxZ
        self.checkedCounter       = None    # int         m_CheckedCounter
        self.regionMin            = None    # float       m_RegionMin[3]       -- The range of nodes.
        self.regionMax            = None    # float       m_RegionMax[3]
        self.cache                = None    # CACHE_ENTRY m_Cache[128]
        self.hashPrimes           = None    # int         m_HashPrimes[16]
        self.hashLinks            = None    # short*      m_pHashLinks
        self.hashLinkCount        = None    # int         m_nHashLinks

        # kinda sleazy. In order to allow variety in active idles for monster
        # groups in a room with more than one node, we keep track of the last
        # node we searched from and store it here. Subsequent searches by other
        # monsters will pick up where the last search stopped
        self.lastActiveIdleSearch = None    # int         m_iLastActiveIdleSearch

        # another such system used to track the search for cover nodes,
        # helps greatly with two monsters trying to get to the same node
        self.lastCoverSearch      = None    # int         m_iLastCoverSearch

    @classmethod
    def fromFile (cls, filePath : str) -> 'Graph':
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData = readBin(filePath)
        reader  = MemReader(rawData, filePath)

        return cls._read(reader)

    @classmethod
    def fromBuffer (cls, rawData : bytes, filePath : str | None = None) -> 'Graph':
        reader = MemReader(rawData, filePath)

        return cls._read(reader)

    @classmethod
    def _read (cls, reader : MemReader) -> 'Graph':
        assert reader.getSize() >= 4 + Graph.SIZE

        graph = Graph()

        graph.filePath = reader.getFilePath()

        cls._readPrimary(reader, graph)
        cls._readNodes(reader, graph)
        cls._readLinks(reader, graph)
        cls._readDistInfos(reader, graph)
        cls._readRouteInfos(reader, graph)
        cls._readHashLinks(reader, graph)

        assert not reader.remaining()

        return graph

    @classmethod
    def _readPrimary (cls, reader : MemReader, graph : 'Graph') -> None:
        graph.version  = reader.i32()

        assert graph.version == GRAPH_VERSION
        assert reader.remaining() >= Graph.SIZE

        start = reader.tell()

        # read CGraph
        graph.isGraphPresent       = reader.skip(4, True)      # BOOL        m_fGraphPresent      -- is the graph in memory?
        graph.isGraphPtrsSet       = reader.skip(4, False)     # BOOL        m_fGraphPointersSet  -- are the entity pointers for the graph all set?
        graph.isRoutingComplete    = reader.skip(4, True)      # BOOL        m_fRoutingComplete   -- are the optimal routes computed, yet?
        graph.nodes                = reader.skip(4)            # CNode*      m_pNodes             -- pointer to the memory block that contains all node info
        graph.links                = reader.skip(4)            # CLink*      m_pLinkPool          -- big list of all node connections
        graph.routeInfos           = reader.skip(4)            # char*       m_pRouteInfo         -- compressed routing information the nodes use.
        graph.nodeCount            = reader.i32()              # int         m_cNodes             -- total number of nodes
        graph.linkCount            = reader.i32()              # int         m_cLinks             -- total number of links
        graph.routeInfoSize        = reader.i32()              # int         m_nRouteInfo         -- size of m_pRouteInfo in bytes.

        # Tables for making the nearest node lookup faster. SortedBy provided nodes in an
        # order of a particular coordinate. Instead of doing a binary search, RangeStart
        # and RangeEnd let you get to the part of SortedBy that you are interested in.
        # Once you have a point of interest, the only way you'll find a closer point is
        # if at least one of the coordinates is closer than the ones you have now. So we
        # search each range. After the search is exhausted, we know we have the closest node
        graph.distInfos            = reader.skip(4)            # DIST_INFO*  m_di                 -- This is m_cNodes long, but the entries don't correspond to CNode entries.

        graph.rangeStart           = [                         # int         m_RangeStart[3][256]
            reader.i32(GRAPH_RANGE_COUNT),
            reader.i32(GRAPH_RANGE_COUNT),
            reader.i32(GRAPH_RANGE_COUNT),
        ]

        graph.rangeEnd             = [                         # int         m_RangeEnd[3][256]
            reader.i32(GRAPH_RANGE_COUNT),
            reader.i32(GRAPH_RANGE_COUNT),
            reader.i32(GRAPH_RANGE_COUNT),
        ]

        graph.shortest             = reader.f32()              # float       m_flShortest
        graph.nearest              = reader.i32()              # int         m_iNearest
        graph.minX                 = reader.i32()              # int         m_minX
        graph.minY                 = reader.i32()              # int         m_minY
        graph.minZ                 = reader.i32()              # int         m_minZ
        graph.maxX                 = reader.i32()              # int         m_maxX
        graph.maxY                 = reader.i32()              # int         m_maxY
        graph.maxZ                 = reader.i32()              # int         m_maxZ
        graph.minBoxX              = reader.i32()              # int         m_minBoxX
        graph.minBoxY              = reader.i32()              # int         m_minBoxY
        graph.minBoxZ              = reader.i32()              # int         m_minBoxZ
        graph.maxBoxX              = reader.i32()              # int         m_maxBoxX
        graph.maxBoxY              = reader.i32()              # int         m_maxBoxY
        graph.maxBoxZ              = reader.i32()              # int         m_maxBoxZ
        graph.checkedCounter       = reader.skip(4, 0)         # int         m_CheckedCounter
        graph.regionMin            = reader.vec3()             # float       m_RegionMin[3]       -- The range of nodes.
        graph.regionMax            = reader.vec3()             # float       m_RegionMax[3]

        graph.cache                = [                         # CACHE_ENTRY m_Cache[128]
            GraphCacheEntry() for _ in range(GRAPH_CACHE_SIZE)
        ]

        for cacheEntry in graph.cache:
            # read NodeGraphCacheEntry
            cacheEntry.vec              = reader.vec3()        # CACHE_ENTRY.vec
            cacheEntry.nearestNodeIndex = reader.i32()         # CACHE_ENTRY.nearestNodeIndex

        graph.hashPrimes           = reader.i32(16)            # int         m_HashPrimes[16]
        graph.hashLinks            = reader.skip(4)            # short*      m_pHashLinks
        graph.hashLinkCount        = reader.i32()              # int         m_nHashLinks

        # kinda sleazy. In order to allow variety in active idles for monster
        # groups in a room with more than one node, we keep track of the last
        # node we searched from and store it here. Subsequent searches by other
        # monsters will pick up where the last search stopped
        graph.lastActiveIdleSearch = reader.i32()              # int         m_iLastActiveIdleSearch

        # another such system used to track the search for cover nodes,
        # helps greatly with two monsters trying to get to the same node
        graph.lastCoverSearch      = reader.i32()              # int         m_iLastCoverSearch

        assert reader.tell() - start == Graph.SIZE

    @classmethod
    def _readNodes (cls, reader : MemReader, graph : 'Graph') -> None:
        assert reader.remaining() >= GraphNode.SIZE * graph.nodeCount

        graph.nodes = [ GraphNode() for _ in range(graph.nodeCount) ]

        start = reader.tell()

        for node in graph.nodes:
            node.origin         = reader.vec3()      # Vector m_vecOrigin      -- location of this node in space
            node.originPeek     = reader.vec3()      # Vector m_vecOriginPeek  -- location of this node (LAND nodes are NODE_HEIGHT higher).
            node.region         = reader.u8(3, 1)    # BYTE   m_Region[3]      -- Which of 256 regions do each of the coordinate belong?
            node.nodeInfo       = reader.i32()       # int    m_afNodeInfo     -- bits that tell us more about this location
            node.linkCount      = reader.i32()       # int    m_cNumLinks      -- how many links this node has
            node.firstLinkIndex = reader.i32()       # int    m_iFirstLink     -- index of this node's first link in the link pool.

            # Where to start looking in the compressed routing table (offset into m_pRouteInfo).
            # (4 hull sizes -- smallest to largest + fly/swim), and secondly, door capability.
            node.nextBestNode   = [                  # int    m_pNextBestNode[MAX_NODE_HULLS][2]
                [
                    reader.i32(),
                    reader.i32(),
                ] for _ in range(GRAPH_MAX_NODE_HULLS)
            ]

            # Used in finding the shortest path. m_fClosestSoFar is -1 if not visited.
            # Then it is the distance to the source. If another path uses this node
            # and has a closer distance, then m_iPreviousNode is also updated.
            node.closestSoFar   = reader.f32()       # float  m_flClosestSoFar -- Used in finding the shortest path.
            node.prevNode       = reader.i32()       # int    m_iPreviousNode
            node.hintType       = reader.i16()       # short  m_sHintType      -- there is something interesting in the world at this node's position
            node.hintActivity   = reader.i16()       # short  m_sHintActivity  -- there is something interesting in the world at this node's position
            node.hintYaw        = reader.f32()       # float  m_flHintYaw      -- monster on this node should face this yaw to face the hint.

        assert reader.tell() - start == GraphNode.SIZE * graph.nodeCount

    @classmethod
    def _readLinks (cls, reader : MemReader, graph : 'Graph') -> None:
        assert reader.remaining() >= GraphLink.SIZE * graph.linkCount

        graph.links = [ GraphLink() for _ in range(graph.linkCount) ]

        start = reader.tell()

        for link in graph.links:
            link.srcNodeIndex   = reader.i32()         # int        m_iSrcNode              -- the node that 'owns' this link ( keeps us from having to make reverse lookups )
            link.dstNodeIndex   = reader.i32(pad=4)    # int        m_iDestNode             -- the node on the other end of the link.
            link.blockEntity    = None                 # entvars_t* m_pLinkEnt              -- the entity that blocks this connection (doors, etc)

            # m_szLinkEntModelname is not necessarily NULL terminated (so we can store it in a more alignment-friendly 4 bytes)
            link.blockModelName = reader.string(4)     # char       m_szLinkEntModelname[4] -- the unique name of the brush model that blocks the connection (this is kept for save/restore)
            link.linkInfo       = reader.i32()         # int        m_afLinkInfo            -- information about this link
            link.ownNodeIndex   = reader.f32()         # float      m_flWeight              -- length of the link line segment

        assert reader.tell() - start == GraphLink.SIZE * graph.linkCount

    @classmethod
    def _readDistInfos (cls, reader : MemReader, graph : 'Graph') -> None:
        assert reader.remaining() >= GraphDistInfo.SIZE * graph.nodeCount

        graph.distInfos = [ GraphDistInfo() for _ in range(graph.nodeCount) ]

        start = reader.tell()

        for info in graph.distInfos:
            info.sortedBy     = reader.i32(3)        # int m_SortedBy[3]
            info.checkedEvent = reader.skip(4, 0)    # int m_CheckedEvent

        assert reader.tell() - start == GraphDistInfo.SIZE * graph.nodeCount

    @classmethod
    def _readRouteInfos (cls, reader : MemReader, graph : 'Graph') -> None:
        assert reader.remaining() >= graph.routeInfoSize

        start = reader.tell()

        graph.routeInfos = reader.i8(graph.routeInfoSize)  # TODO: is i8 or u8 or bytes???

        assert reader.tell() - start == graph.routeInfoSize

    @classmethod
    def _readHashLinks (cls, reader : MemReader, graph : 'Graph') -> None:
        assert reader.remaining() >= 2 * graph.hashLinkCount  # 2 is the short type size

        start = reader.tell()

        graph.hashLinks = reader.i16(graph.hashLinkCount)  # TODO: is i16 or u16???

        assert reader.tell() - start == 2 * graph.hashLinkCount  # 2 is the short type size



# noinspection PyUnusedLocal
def _test_ ():
    for filePath in iterFiles(GRAPHS_DIR, False, [ GRAPH_EXT ]):
        print(filePath, '\n')

        graph = Graph.fromFile(filePath)
        graph = Graph.fromBuffer(readBin(filePath), filePath)

        for link in graph.links:
            if link.blockModelName.strip():
                print(link.blockModelName)

        print(' ')



__all__ = [
    'Graph',
    'GraphDistInfo',
    'GraphLink',
    'GraphNode',
    'GraphCacheEntry',

    '_test_',
]



if __name__ == '__main__':
    _test_()
