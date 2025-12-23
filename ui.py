import gradio as gr

def sql_ui(orchestrator):
    """Create the CSV to SQL tab UI with exact workflow"""
    
    with gr.Tab("📊 CSV to SQL"):
        gr.Markdown("### Store CSV Data in SQL Database")
        gr.Markdown("Upload CSV files and store them in a SQLite database.")
        
        with gr.Row():
            # Left column - Upload and controls
            with gr.Column(scale=1):
                csv_input = gr.File(
                    label="Upload CSV File",
                    file_types=[".csv"],
                    type="filepath"
                )
                
                table_dropdown = gr.Dropdown(
                    choices=orchestrator.process_csv("get"),
                    value="+ Create New Table",
                    label="Select Table",
                    interactive=True,
                    info="Choose existing table or create new one"
                )
                
                new_table_input = gr.Textbox(
                    label="New Table Name (if creating new)",
                    placeholder="e.g., sales_data, customers, products",
                    visible=True
                )
                
                preview_limit = gr.Slider(
                    minimum=5,
                    maximum=100,
                    value=10,
                    step=5,
                    label="Preview Rows",
                    info="Number of rows to display per table"
                )
                
                with gr.Row():
                    store_btn = gr.Button("Store CSV", variant="primary", size="lg")
                    refresh_btn = gr.Button("Refresh", size="lg")
                
                status_output = gr.Textbox(
                    label="Status",
                    lines=4,
                    interactive=False
                )
            
            # Right column - Data preview
            with gr.Column(scale=2):
                gr.Markdown("### Database Content")
                data_summary = gr.Textbox(
                    label="#### Table Summary",
                    lines=4,
                    interactive=False,
                )
                data_preview = gr.Dataframe(
                    label="#### Table Preview",
                    interactive=False,
                    wrap=True
                )
                
        # Showing Refresh Function
        def toggle_new_table_input(selected):
            if selected == "+ Create New Table":
                return gr.update(visible=True)
            return gr.update(visible=False)
        

        def refresh_table(table, limit):
            if table == "+ Create New Table":
                return "No table selected", None
            return orchestrator.process_csv("refresh", selected_table=table, limit=limit)
        
        # Button

        table_dropdown.change(
            fn=toggle_new_table_input,
            inputs=[table_dropdown],
            outputs=[new_table_input]
        )

        store_btn.click(
            fn=lambda file, table, new_name, limit: orchestrator.process_csv("store", file, table, new_name, limit),
            inputs=[csv_input, table_dropdown, new_table_input, preview_limit],
            outputs=[status_output, table_dropdown, data_summary, data_preview]
        )
        
        refresh_btn.click(
            fn=refresh_table,
            inputs=[table_dropdown, preview_limit],
            outputs=[data_summary, data_preview]
        )

def indexing_ui(orchestrator):
    with gr.Tab("📥 Indexing"):
        gr.Markdown("### Convert PDF to Vector")
        gr.Markdown("Upload a PDF file to process and index it.")
        
        with gr.Row():
            with gr.Column(scale=1):
                collection_list = gr.Dropdown(
                    choices=orchestrator.get_collections_from_db(),
                    value="+ Create New Collection",
                    label="Select Collection",
                    interactive=True,
                    info="Choose existing collection or create new one"
                )
                
                new_collection_input = gr.Textbox(
                    label="New collection Name (if creating new)",
                    placeholder="e.g., ABC Company, Client X, Policy Guidelines",
                    visible=True
                )

                file_input = gr.File(
                    label="Upload PDF",
                    file_types=[".pdf"],
                    type="filepath"
                )
                index_btn = gr.Button("🔄 Index Document", variant="primary", size="lg")
            
            with gr.Column(scale=3):
                index_preview = gr.Textbox(
                    label="Text Preview",
                    lines=5,
                    interactive=False
                )
                index_output = gr.Textbox(
                    label="Indexing Status",
                    lines=5,
                    interactive=False
                )
    
    chunked_text = gr.State()
    collection_name = gr.State()

    def determine_collection(collection_dropdown, new_collection_name):
        return new_collection_name if collection_dropdown == "+ Create New Collection" else collection_dropdown
    
    def refresh_collections():
        collections = orchestrator.get_collections_from_db()
        print(f"refresh_collections: {collections}")
        # Return dropdown update with new choices
        return gr.Dropdown(choices=collections, value="+ Create New Collection")

    def toggle_new_table_input(selected):
        if selected == "+ Create New Collection":
            return gr.update(visible=True)
        return gr.update(visible=False)
    
    collection_list.change(
        fn=toggle_new_table_input,
        inputs=[collection_list],
        outputs=[new_collection_input]
    )

    index_btn.click(
        fn=orchestrator.process_pdf,
        inputs=[file_input],
        outputs=[index_output, index_preview]
    ).then(
        fn=orchestrator.chunking_text,
        inputs=[file_input], 
        outputs=[index_output, chunked_text]
    ).then(
        fn=determine_collection,
        inputs=[collection_list, new_collection_input],
        outputs=[collection_name]
    ).then(
        fn=orchestrator.upserting_docs,
        inputs=[index_output, file_input, chunked_text, collection_name],
        outputs=[index_output]
    ).then(
        fn=refresh_collections,
        inputs=None,
        outputs=[collection_list]
    )

def retrieval_ui(orchestrator):
    with gr.Tab("🔍 Retrieval"):
        gr.Markdown("### Query Indexed Documents")
        gr.Markdown("Search through your indexed documents.")
        
        with gr.Row():
            with gr.Column():
                collection_selector = gr.Dropdown(
                    choices=orchestrator.get_collections_from_db(),
                    label="Select Collection",
                    interactive=True
                )
                refresh_btn = gr.Button("🔄 Refresh", size="sm")
                
                file_selector = gr.Dropdown(
                    choices=[],
                    label="Select Document (leave empty to search all)",
                    interactive=True
                )
                doc_id_state = gr.State({})
                
                query_input = gr.Textbox(
                    label="Enter your query",
                    placeholder="Ask Something...",
                    lines=3
                )
                retrieve_btn = gr.Button("🔍 Retrieve", variant="primary", size="lg")
            
            css = """
                .markdown {
                    max-height: 400px;
                    overflow-y: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
                """
            with gr.Blocks(css=css):
                with gr.Column():
                    retrieval_output = gr.Markdown(label="Retrieval Results")

    def refresh_collection_dropdown():
        collections = orchestrator.get_collections_from_db()
        print(f"refresh_collection_dropdown: {collections}")
        return gr.Dropdown(choices=collections)

    def update_file_choices(collection_name):
        print(f"DEBUG update_file_choices: collection_name={collection_name}")
        if collection_name and collection_name != "+ Create New Collection":
            documents = orchestrator.get_documents_by_collection(collection_name)
            print(f"DEBUG documents: {documents}")
            
            doc_mapping = {}
            choices = []
            
            for doc_id, filename in documents:
                display_text = f"{filename} - {{{doc_id}}}"
                choices.append(display_text)
                doc_mapping[display_text] = doc_id
            
            print(f"DEBUG choices: {choices}")
            print(f"DEBUG doc_mapping: {doc_mapping}")
            return gr.Dropdown(choices=choices, value=None), doc_mapping
        
        return gr.Dropdown(choices=[], value=None), {}
    
    # Refresh button to manually update collections
    refresh_btn.click(
        fn=refresh_collection_dropdown,
        inputs=None,
        outputs=[collection_selector]
    )
    
    collection_selector.change(
        fn=update_file_choices,
        inputs=[collection_selector],
        outputs=[file_selector, doc_id_state]
    )

    def retrieve_with_doc_id(query, collection_name, document_selector, doc_mapping):
        doc_id = None
        print(f"DEBUG retrieve: document_selector={document_selector}, doc_mapping={doc_mapping}")
        
        if document_selector and document_selector in doc_mapping:
            doc_id = doc_mapping[document_selector]
        
        print(f"DEBUG: Retrieving query='{query}', collection='{collection_name}', doc_id='{doc_id}'")
        return orchestrator.retrieve_document(query, collection_name, doc_id)

    retrieve_btn.click(
        fn=retrieve_with_doc_id,
        inputs=[query_input, collection_selector, file_selector, doc_id_state],
        outputs=[retrieval_output]
    )