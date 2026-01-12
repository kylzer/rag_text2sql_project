from database.to_sql import CSVToSQL
from model import TabularStoringResponse, DatabaseSchema

import os
import json
import gradio as gr

from utils import langchainInvoke

class TabularOrchestrator:
    def __init__(self, db_folder, db_name):
        self.db_folder = db_folder 
        self.db_name = db_name     

        self.db_path = f"{db_folder}{db_name}"      
        os.makedirs(db_folder, exist_ok=True)

        self.sql_handler = CSVToSQL(self.db_path)
    
    def response(self, message, table, summary="", preview=None):
        """Modelling response output"""
        r = TabularStoringResponse(message, self.update_dropdown(self.get_table_choices(), table), summary, preview)
        return r.status, r.dropdown, r.summary, r.preview

    def update_dropdown(self, choices, value):
        """Update dropdown list"""
        return gr.update(choices=choices, value=value)
    
    def get_table_choices(self):
        """Get tables dropwdown"""
        if not os.path.exists(self.db_path):
            return ["+ Create New Table"]
        
        tables = self.sql_handler.get_db_tables()
        
        if not tables:
            return ["+ Create New Table"]        
        return tables + ["+ Create New Table"]
    
    def store_csv(self, file, selected_table, new_table_name, preview_limit):
        """Store CSV to database"""
        if file is None:
            return self.response("No file uploaded!", selected_table)
        
        try:
            if selected_table == "+ Create New Table":
                if not new_table_name or new_table_name.strip() == "":
                    return self.response("Please provide a table name!", selected_table)
                
                table_name = new_table_name.strip().replace(" ", "_").replace("-", "_")                
                success, message = self.sql_handler.create_table_from_csv(file, table_name)
                
                if not success:
                    return self.response(f"{message}", selected_table)
                                
            else:
                table_name = selected_table
                success, message = self.sql_handler.append_to_table(file, table_name)
                
                if not success:
                    return self.response(f"{message}", selected_table)
            schema_status = "Generate Schema Success" if self.extract_schema() else "Error while generating schema"
            print("Schema Status : ", schema_status)
            summary, preview = self.sql_handler.get_table_preview(table_name, preview_limit)
            return self.response(message, selected_table, summary, preview)
                        
        except Exception as e:
            return self.response(f"Error: {str(e)}", selected_table)
    
    def refresh_data_view(self, table, preview_limit):
        """Refresh showing data"""
        summary, preview = self.sql_handler.get_table_preview(table, preview_limit)
        return summary, preview
    
    def extract_schema(self):
        try:
            conn = self.sql_handler.get_connection()
            database_name = self.db_name
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name NOT LIKE 'sqlite_%';
            """)
            tables = [row[0] for row in cursor.fetchall()]

            table_list = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
                table_list[table] = {col: "Description Placeholder" for col in columns}
            
            conn.close()
            
            schema = {
                "database_name": database_name,
                "table_list": table_list
            }
            print(f"Initial Schema :\n{schema}")

            restructured_status = self.generate_description(schema)
            
            return restructured_status
        except Exception as e:
            print(f"Error while generate description for Schema with error: {str(e)}")
            return False
    
    def generate_description(self, schema):
        try:
            print("Generating Schema Description!")
            db_name = schema['database_name']
            table_list = schema['table_list']

            DESCRIPTION_SYSTEM_PROMPT = """
                Given this database schema, provide clear, concise descriptions for each table and column.
                The descriptions should help with text-to-SQL generation.

                Return ONLY a valid JSON object in this exact format (no markdown, no explanation):
                {{
                    database_name: name of the database,
                    database_desc: description of the database,
                    table_list: {{
                        table_name: {{
                            table_desc: description of the table
                            columns: {{
                                column_name: description of the column
                            }}
                        }}
                    }}
                }}
            """
            DESCRIPTION_USER_PROMPT = """
                Please generate a description for each column based on this information.

                Database Name : {db_name}
                Table & Column List
                <table>
                {table_list}
                </table>
            """

            restructured_schema = langchainInvoke(DESCRIPTION_SYSTEM_PROMPT, DESCRIPTION_USER_PROMPT, {'db_name':db_name, 'table_list':table_list}, DatabaseSchema).model_dump()
            with open(f"{self.db_folder}/db_schema.json", "w", encoding="utf-8") as f:
                json.dump(restructured_schema, f, indent=2)
            return True
        except Exception as e:
            print(f"Error while generate description for Schema with error: {str(e)}")
            return False
