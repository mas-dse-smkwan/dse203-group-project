from .datasources import AsterixSource
from .logger import log

class Categories(AsterixSource):

    def __init__(self, asterix_config):
        AsterixSource.__init__(self,asterix_config)
        self._fields = '''
            ci.classification,
            ci.nodeID AS node_id,
            ci.category.level_0 AS level_0,
            ci.category.nested.level_1 AS level_1,
            ci.category.nested.nested.level_2 AS level_2,
            ci.category.nested.nested.nested.level_3 AS level_3,
            ci.category.nested.nested.nested.nested.level_4 AS level_4,
            ci.category.nested.nested.nested.nested.nested.level_5 AS level_5'''

    @log
    def search(self, string_search = '', classfication_only=False):
        query = '''
            SELECT '''+ self._fields + '''
            FROM ClassificationInfo ci
            WHERE ci.category.level_0 LIKE "%{search}%"
                or ci.category.nested.level_1 LIKE "%{search}%"
                or ci.category.nested.nested.level_2 LIKE "%{search}%"
                or ci.category.nested.nested.nested.level_3 LIKE "%{search}%"
                or ci.category.nested.nested.nested.nested.level_4 LIKE "%{search}%"
                or ci.category.nested.nested.nested.nested.nested.level_5 LIKE "%{search}%";'''

        return self._execSqlPpQuery(query, {'search':string_search})
    
    
        
    def parentOf_depth1(self, node_id, depth = None):
        return self.query('''
            SELECT
                CASE WHEN ci.category.nested.nested.level_2 = "N/A" THEN
                    (SELECT VALUE c.nodeID
                    FROM ClassificationInfo c
                    WHERE ci.category.level_0 = c.category.level_0 
                        and c.category.nested.level_1 = "N/A")
                WHEN ci.category.nested.nested.nested.level_3 = "N/A" THEN
                    (SELECT VALUE c.nodeID
                    FROM ClassificationInfo c
                    WHERE ci.category.level_0 = c.category.level_0
                        and ci.category.nested.level_1 = c.category.nested.level_1
                        and c.category.nested.nested.level_2 = "N/A")
                WHEN ci.category.nested.nested.nested.nested.level_4 = "N/A" THEN
                    (SELECT VALUE c.nodeID
                    FROM ClassificationInfo c
                    WHERE ci.category.level_0 = c.category.level_0
                        and ci.category.nested.level_1 = c.category.nested.level_1
                        and ci.category.nested.nested.level_2 = c.category.nested.nested.level_2
                        and c.category.nested.nested.nested.level_3 = "N/A")
                WHEN ci.category.nested.nested.nested.nested.nested.level_5 = "N/A" THEN
                    (SELECT VALUE c.nodeID
                    FROM ClassificationInfo c
                    WHERE ci.category.level_0 = c.category.level_0
                        and ci.category.nested.level_1 = c.category.nested.level_1
                        and ci.category.nested.nested.level_2 = c.category.nested.nested.level_2
                        and ci.category.nested.nested.nested.level_3 = c.category.nested.nested.nested.level_3
                        and c.category.nested.nested.nested.nested.level_4 = "N/A")                
                ELSE 
                    (SELECT VALUE c.nodeID
                    FROM ClassificationInfo c
                    WHERE ci.category.level_0 = c.category.level_0 
                        and ci.category.nested.level_1 = c.category.nested.level_1 
                        and ci.category.nested.nested.level_2 = c.category.nested.nested.level_2
                        and ci.category.nested.nested.nested.level_3 = c.category.nested.nested.nested.level_3
                        and ci.category.nested.nested.nested.nested.level_4 = c.category.nested.nested.nested.nested.level_4
                        and c.category.nested.nested.nested.nested.nested.level_5 = "N/A")  
                END AS parents
        FROM ClassificationInfo ci
        WHERE ci.nodeID = {};'''.format(node_id))

    def parentsOf(self, node_id, depth = None):
        return self._execSqlPpQuery('''
            with node_info as (
                SELECT
                    ci.nodeID,
                    CASE
                        WHEN
                            ci.category.level_0 <> "N/A"
                            AND ci.category.nested.level_1 = "N/A"
                        THEN 0
                        WHEN
                            ci.category.nested.level_1 <> "N/A"
                            AND ci.category.nested.nested.level_2 = "N/A"
                        THEN 1
                        WHEN
                            ci.category.nested.nested.level_2 <> "N/A"
                            AND ci.category.nested.nested.nested.level_3  = "N/A"
                        THEN 2
                        WHEN
                            ci.category.nested.nested.nested.level_3  <> "N/A"
                            AND ci.category.nested.nested.nested.nested.level_4 = "N/A"
                        THEN 3
                        WHEN
                            ci.category.nested.nested.nested.nested.level_4 <> "N/A"
                            AND ci.category.nested.nested.nested.nested.nested.level_5 = "N/A"
                        THEN 4
                        WHEN ci.category.nested.nested.nested.nested.nested.level_5 <> "N/A"
                        THEN 5
                    END as level,
                    ci.category.level_0 AS level_0,
                    ci.category.nested.level_1 AS level_1,
                    ci.category.nested.nested.level_2 AS level_2,
                    ci.category.nested.nested.nested.level_3 AS level_3,
                    ci.category.nested.nested.nested.nested.level_4 AS level_4,
                    ci.category.nested.nested.nested.nested.nested.level_5 AS level_5
                FROM ClassificationInfo ci
                WHERE
                    ci.nodeID = {node_id}
            )[0]
            SELECT
                node_info.nodeID as node_id,
                node_info.level as level,
                ci.nodeID as parent_node_id
            FROM ClassificationInfo ci
            WHERE
                 (
                    node_info.level = 0
                    AND 1 = -1
                 )
                 OR (
                    node_info.level = 1
                    AND ci.category.level_0 = node_info.level_0
                    AND ci.category.nested.level_1 = "N/A"
                 )
                 OR (
                    node_info.level = 2
                    AND ci.category.nested.level_1 = node_info.level_1
                    AND ci.category.nested.nested.level_2 = "N/A"
                 )
                 OR (
                    node_info.level = 3
                    AND ci.category.nested.nested.level_2 = node_info.level_2
                    AND ci.category.nested.nested.nested.level_3 = "N/A"
                 )
                 OR (
                    node_info.level = 4
                    AND ci.category.nested.nested.nested.level_3 = node_info.level_3
                    AND ci.category.nested.nested.nested.nested.level_4 = "N/A"
                 )
                 OR (
                    node_info.level = 5
                    AND ci.category.nested.nested.nested.nested.level_4 = node_info.level_4
                    AND ci.category.nested.nested.nested.nested.nested.level_5 = "N/A"
                 );''',{'node_id':node_id})