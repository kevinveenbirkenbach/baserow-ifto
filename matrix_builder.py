from data_processor import DataProcessor
class MatrixBuilder:
    def __init__(self, data_processor, verbose=False):
        self.data_processor = data_processor
        self.verbose = verbose

    def print_verbose_message(self, message):
        if self.verbose:
            print(message)
            
    def build_multitable_matrix(self, tables_data):
        original_keys=list(tables_data.keys())
        for table_name, table_rows in tables_data.copy().items():
            self.build_matrix(tables_data,table_name, table_rows)
        
        matrix={}
        for key in original_keys:
            matrix[key]=tables_data[key]
        return matrix
            
    def build_matrix(self, tables_data, table_name, table_rows, reference_map={}):
        """Build a matrix with linked rows filled recursively."""
        reference_map_child = reference_map.copy()
        self.process_link_fields(table_name, tables_data, reference_map_child)
        self.fill_cells_with_related_content(tables_data,table_name, table_rows, reference_map_child)

        return tables_data

    def fill_cells_with_related_content(self, tables_data, table_name, table_rows, reference_map_child):
        """Fill cells with related content."""
        for table_row in table_rows:
            self.print_verbose_message(f"table_row: {table_row}")
            for table_column_name, table_cell_content in table_row.items():
                self.print_verbose_message(f"table_cell_content {table_cell_content}")
                if table_column_name in reference_map_child:
                    
                    link_row_table_id = reference_map_child[table_column_name]["link_row_table_id"]
                    self.print_verbose_message(f"link_row_table_id: {link_row_table_id}")
                    
                    link_row_related_field_id = reference_map_child[table_column_name]["link_row_related_field_id"]
                    self.print_verbose_message(f"link_row_related_field_id: {link_row_related_field_id}")
                    # This could be wrong:
                    if link_row_related_field_id:
                        new_content = []
                        for entry_id, entry_content in table_cell_content:
                            self.print_verbose_message(f"entry_content {entry_content}")

                            related_cell_identifier = self.generate_related_cell_identifier(link_row_table_id, link_row_related_field_id, entry_id)
                            self.print_verbose_message(f"related_cell_identifier: {related_cell_identifier}")

                            if related_cell_identifier in reference_map_child[table_column_name]["embeded"]:
                                self.print_verbose_message(f"Skipped {related_cell_identifier}. Already implemented")
                                continue
                                
                                reference_map_child[table_column_name]["embeded"].append(related_cell_identifier)
                                self.build_matrix(tables_data, link_row_table_id, tables_data[link_row_table_id], reference_map_child)
                                new_content.append(entry_content)  # Append the original content or modify as needed
                        table_row[table_column_name] = new_content

    def generate_related_cell_identifier(self, table_id, table_column_id, table_row_id):
        return self.generate_cell_identifier(table_id, "field_" + str(table_column_id), table_row_id);

    def generate_cell_identifier(self, table_name, table_column_name, table_row_id):
        table_name=str(table_name)    
        table_column_name=str(table_column_name)    
        table_row_id=str(table_row_id)    
        return "table_" + table_name + "_" + table_column_name + "_row_" + table_row_id

    def process_link_fields(self, table_name, tables_data, reference_map_child):
        """Process link fields for a given table."""
        link_fields = self.data_processor.get_link_fields_for_table(table_name)

        for link_field in link_fields:
            self.load_table_data_if_not_present(link_field, tables_data)
            self.update_reference_map(link_field, reference_map_child)

    def load_table_data_if_not_present(self, link_field, tables_data):
        """Load table data if it's not already loaded."""
        link_row_table_id = link_field["link_row_table_id"]

        if link_row_table_id not in tables_data:
            tables_data[link_row_table_id] = self.data_processor.get_all_rows_from_table(link_row_table_id)

    def update_reference_map(self, link_field, reference_map_child):
        """Update the reference map with the link field data."""
        link_field_name = "field_" + str(link_field["id"])

        if link_field_name not in reference_map_child:
            reference_map_child[link_field_name] = link_field
            reference_map_child[link_field_name]["embeded"] = []