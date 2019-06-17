class BulkInsert(object):
    def __init__(self, con):
        self.con = con

    def execute(self, insert_data, target_table, col_names):

        if len(insert_data) == 0:
            return None

        try:
            cursor = self.con.cursor()
            query = self._generate_query(col_names, cursor, insert_data, target_table)
            cursor.execute(query)
            self.con.commit()
        except Exception as e:
            raise RuntimeError()

    def _generate_query(self, col_names, cursor, insert_data, target_table):
        place_holder, schema = self._generate_place_holder_and_schema(col_names)
        data_text = ','.join(cursor.mogrify(place_holder, row) for row in insert_data)
        return 'INSERT INTO ' + target_table + schema + ' VALUES ' + data_text

    @staticmethod
    def _generate_place_holder_and_schema(col_names):
        buf = ['%s'] * len(col_names)
        place_holder = '(' + ', '.join(buf) + ')'
        schema = '(' + ', '.join(map(lambda x: str(x), col_names)) + ')'
        return place_holder, schema
