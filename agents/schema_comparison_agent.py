import logging
import json


class DummyDBInterface:
    def execute_query(self, query):
        logging.info("Executing query: %s", query)
        return [
            {'column_name': 'id', 'data_type': 'INTEGER'},
            {'column_name': 'name', 'data_type': 'TEXT'}
        ]


class SchemaComparisonAgent:
    """
    Compares the structured JSON data against the current database schema.
    For each key in the structured JSON that does not exist in the schema,
    it infers the PostgreSQL data type and generates an SQL statement to add the column.
    It also creates mapping instructions for downstream agents.
    """

    def __init__(self, db_interface, table_name="data_table", logger=None):
        self.db_interface = db_interface
        self.table_name = table_name
        self.logger = logger or logging.getLogger(__name__)

    def fetch_current_schema(self):
        query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{self.table_name}';
        """
        try:
            result = self.db_interface.execute_query(query)
            current_schema = {row['column_name']
                : row['data_type'] for row in result}
            self.logger.info("Current schema fetched: %s", current_schema)
            return current_schema
        except Exception as e:
            self.logger.error("Error fetching current schema: %s", e)
            return {}

    def infer_data_type(self, value):
        if isinstance(value, int):
            return 'INTEGER'
        elif isinstance(value, float):
            return 'FLOAT'
        elif isinstance(value, bool):
            return 'BOOLEAN'
        elif isinstance(value, (dict, list)):
            return 'JSONB'
        else:
            return 'TEXT'

    def compare_schema(self, structured_json, current_schema):
        schema_updates = {}
        mapping_instructions = {}
        for key, value in structured_json.items():
            if key not in current_schema:
                inferred_type = self.infer_data_type(value)
                schema_updates[key] = inferred_type
                mapping_instructions[key] = f"New column to be added with type {inferred_type}"
            else:
                mapping_instructions[key] = f"Existing column of type {current_schema[key]}"
        self.logger.info("Schema updates determined: %s", schema_updates)
        self.logger.info("Mapping instructions: %s", mapping_instructions)
        return schema_updates, mapping_instructions

    def generate_schema_update_instructions(self, schema_updates):
        instructions = []
        for column, data_type in schema_updates.items():
            sql = f"ALTER TABLE {self.table_name} ADD COLUMN {column} {data_type};"
            instructions.append(sql)
        self.logger.info(
            "Generated schema update instructions: %s", instructions)
        return instructions

    def execute(self, state):
        structured_data = state.get("structured_data")
        if not structured_data:
            self.logger.error("No 'structured_data' provided in state.")
            return state

        current_schema = state.get("current_db_info")
        if not current_schema:
            current_schema = self.fetch_current_schema()

        schema_updates, mapping_instructions = self.compare_schema(
            structured_data, current_schema)
        schema_update_instructions = self.generate_schema_update_instructions(
            schema_updates)

        state["schema_update_instructions"] = schema_update_instructions
        state["mapping_instructions"] = mapping_instructions

        new_schema = current_schema.copy()
        new_schema.update(schema_updates)
        state["current_db_info"] = new_schema

        self.logger.info("Schema comparison complete. Updates added to state.")
        return state


def schema_comparison_agent(state):
    db_interface = DummyDBInterface()
    agent = SchemaComparisonAgent(
        db_interface=db_interface, table_name="data_table")
    return agent.execute(state)
