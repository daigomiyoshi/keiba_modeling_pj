class BulkInsert(object):
    def __init__(self, con):
        self.con = con

    def execute(self, insert_data, target_table, col_names):
        if len(insert_data) == 0:
            return None

        try:
            cursor = self.con.cursor()
            query = self._generate_query(col_names, insert_data, target_table)
            cursor.execute(query)
            self.con.commit()
        except Exception:
            raise RuntimeError()

    @staticmethod
    def _generate_query(col_names, insert_data, target_table):
        schema = '(' + ', '.join(map(lambda x: str(x), col_names)) + ')'
        data_text = ', '.join(map(lambda x: str(tuple(x)), insert_data))
        return 'INSERT INTO ' + target_table + schema + ' VALUES ' + data_text
