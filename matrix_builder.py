from data_processor import DataProcessor

class MatrixBuilder:
    def __init__(self, data_processor, tables_data, verbose=False):
        self.data_processor = data_processor
        self.tables_data = tables_data
        self.lazy_loaded_tables_data = {}  # Neue Arbeitsvariable
        self.verbose = verbose
        self.matrix = {}  # Klassenvariable

    def build_multitable_matrix(self):
        for table_name, table_rows in self.tables_data.items():
            self.print_verbose_message(f"Building matrix for table: {table_name}")
            self.matrix[table_name] = self._build_matrix_for_table(table_name, table_rows.copy())
        return self.matrix

    def _build_matrix_for_table(self, table_name, table_rows, reference_map={}):
        self.print_verbose_message(f"Starting matrix build for table: {table_name}")
        self.matrix[table_name] = table_rows
        reference_map = reference_map.copy()
        self._process_link_fields(table_name, reference_map)
        self._populate_matrix_with_related_content(table_name, table_rows, reference_map)
        return self.matrix[table_name]

    def _populate_matrix_with_related_content(self, table_name, table_rows, reference_map):
        for table_row in table_rows:
            for column_name, cell_content in table_row.items():
                if column_name in reference_map:
                    self.print_verbose_message(f"Handling linked content for column: {column_name}")
                    self._handle_linked_content(table_row, column_name, cell_content, reference_map)

    def _handle_linked_content(self, table_row, column_name, cell_content, reference_map):
        link_table_id = reference_map[column_name]["link_row_table_id"]
        link_field_id = reference_map[column_name]["link_row_related_field_id"]

        if not link_field_id:
            raise Exception("link_row_related_field_id has to be a positive number")

        self.print_verbose_message(f"Fetching related content for table ID: {link_table_id} and field ID: {link_field_id}")
        new_content = self._fetch_related_content(cell_content, link_table_id, link_field_id, reference_map)
        table_row[column_name] = new_content

    def _fetch_related_content(self, cell_content, link_table_id, link_field_id, reference_map):
        new_content = []
        for entry in cell_content:
            related_cell_id = self._generate_related_cell_identifier(link_table_id, link_field_id, entry["id"])
            self.print_verbose_message(f"Generated related cell identifier: {related_cell_id}")
            if related_cell_id not in reference_map.get("embeded", []):
                reference_map.setdefault("embeded", []).append(related_cell_id)
                self.matrix[link_table_id] = self._build_matrix_for_table(link_table_id, self.lazy_loaded_tables_data.get(link_table_id, []).copy(), reference_map)
                new_content.append(entry)
        return new_content

    def _generate_related_cell_identifier(self, table_id, column_id, row_id):
        return f"table_{table_id}_field_{column_id}_row_{row_id}"

    def _process_link_fields(self, table_name, reference_map):
        link_fields = self.data_processor.get_link_fields_for_table(table_name)
        for link_field in link_fields:
            self.print_verbose_message(f"Processing link fields for table: {table_name}")
            self._load_table_data_if_missing(link_field)
            self._update_reference_map(link_field, reference_map)

    def _load_table_data_if_missing(self, link_field):
        link_table_id = link_field["link_row_table_id"]
        if link_table_id not in self.lazy_loaded_tables_data:
            self.print_verbose_message(f"Loading data for missing table ID: {link_table_id}")
            self.lazy_loaded_tables_data[link_table_id] = self.data_processor.get_all_rows_from_table(link_table_id)

    def _update_reference_map(self, link_field, reference_map):
        field_name = f"field_{link_field['id']}"
        if field_name not in reference_map:
            self.print_verbose_message(f"Updating reference map for field: {field_name}")
            reference_map[field_name] = link_field
            reference_map[field_name]["embeded"] = []

    def print_verbose_message(self, message):
        if self.verbose:
            print(message)
