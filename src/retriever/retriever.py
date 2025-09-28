import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from loguru import logger
from collections import defaultdict

from src.common.config import settings
from src.retriever.data_processor import process_financial_table, process_cap_table
from src.common.schema import Document, TableMetadata

class Retriever:
    def __init__(self, embedding_model_name: str = settings.EMBEDDING_MODEL):
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.documents: Dict[int, Document] = {}

        # Inverted index store for fast filtering
        self.company_index: Dict[str, List[int]] = defaultdict(list)
        self.table_index: Dict[str, List[int]] = defaultdict(list)

        # Vector store of embeddings
        self.faiss_index: faiss.Index = None

        # Load or build the index
        if settings.METADATA_PATH.exists() and settings.FAISS_INDEX_PATH.exists():
            logger.info("Loading index from checkpoints...")
            self._load_from_checkpoints()
        else:
            logger.info("No checkpoints found. Building index from source data...")
            self._build_from_scratch()

    def _build_from_scratch(self):
        """Builds the entire index from the raw JSON data."""
        
        # Load and parse the raw data
        self.parse_raw_data()

        # Create Embeddings
        logger.info("Creating vector embeddings for all documents...")
        embeddings = self._create_embeddings()

        # Build FAISS Index
        logger.info("Building FAISS index...")
        self._build_faiss_index(embeddings)

        # Save Checkpoints
        self._save_checkpoints()
        logger.success("Index build complete and checkpoints saved.")

    def parse_raw_data(self):
        """
        Parses the raw JSON data and processes each table into Document objects.
        """
        # Load Data from JSON
        logger.info(f"Loading data from {settings.DATA_PATH}...")
        with open(settings.DATA_PATH, 'r') as f:
            raw_data = json.load(f)
        
        company_financials = raw_data.get("company_financials")
        if not company_financials:
            raise ValueError("Source data does not contain 'company_financials' key.")
        
        doc_id_counter = 0
        
        TABLE_TITLE_MAP = {
            "key_financials": {"title": "Key Financials"},
            "cash_flow_and_leverage": {"title": "Cash Flow and Leverage"},
            "cap_table": {"title": "Capitalization Table"}
        }
        
        TABLE_PROCESSOR_MAP = {
            "key_financials": process_financial_table,
            "cash_flow_and_leverage": process_financial_table,
            "cap_table": process_cap_table
        }

        for company in company_financials:
            company_info = {
                "name": company.get("company"),
                "id": company.get("company_id"),
                "currency": company.get("currency"),
                "periods": company.get("periods", [])
            }

            if not company_info["name"] or not company_info["id"]:
                logger.warning(f"Skipping company with missing name or ID: {company_info}")
                continue

            logger.debug(f"Processing company: {company_info['name']} (ID: {company_info['id']})")
            
            for table_name, table_data in company.items():
                if table_name in TABLE_PROCESSOR_MAP:
                    processor_func = TABLE_PROCESSOR_MAP[table_name]
                    table_title = TABLE_TITLE_MAP[table_name]
                    
                    # Call the specialized processor
                    content, metadata = processor_func(company_info, table_name, table_data, table_title)
                    
                    # --- Assemble the final Document object ---
                    tableMetadata = TableMetadata(**metadata)

                    doc = Document(
                        doc_id=doc_id_counter,
                        content=content,
                        metadata=tableMetadata
                    )
                    self.documents[doc_id_counter] = doc
                    self.company_index[company_info['name']].append(doc_id_counter)
                    self.table_index[table_name].append(doc_id_counter)

                    doc_id_counter += 1

        logger.info(f"Processed a total of {len(self.documents)} documents from {len(company_financials)} companies.")

    def _create_embeddings(self) -> np.ndarray:
        """Generates embeddings for all documents' content."""
        contents = [doc.content for doc in self.documents.values()]
        logger.info(f"Generating embeddings for {len(contents)} documents...")
        logger.debug(f"Sample content for embedding: {contents[0][:100]}...")

        return self.embedding_model.encode(contents, batch_size=32, show_progress_bar=True, convert_to_numpy=True)

    def _build_faiss_index(self, embeddings: np.ndarray):
        """Creates and populates the FAISS index."""
        dimension = embeddings.shape[1]

        # Using IndexFlatL2 for simplicity that performs exact L2 distance search; ANN/HNSW can be used for larger datasets
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index = faiss.IndexIDMap(self.faiss_index)
        
        # The IDs in the FAISS index are the doc_ids
        ids = np.array(list(self.documents.keys()), dtype='int64')
        self.faiss_index.add_with_ids(embeddings, ids)


    def _save_checkpoints(self):
        """Saves the metadata and FAISS index to disk."""
        logger.info(f"Saving checkpoints to {settings.CHECKPOINT_DIR}...")
        
        # Save metadata
        checkpoint_data = {
            "documents": [doc.model_dump() for doc in self.documents.values()],
            "company_index": self.company_index,
            "table_index": self.table_index
        }
        with open(settings.METADATA_PATH, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        # Save FAISS index
        faiss.write_index(self.faiss_index, str(settings.FAISS_INDEX_PATH))

        logger.success("Checkpoints saved successfully.")

    def _load_from_checkpoints(self):
        """Loads metadata and FAISS index from disk."""
        logger.info("Loading index from checkpoints...")
    
        self.faiss_index = faiss.read_index(str(settings.FAISS_INDEX_PATH))

        with open(settings.METADATA_PATH, 'r') as f:
            checkpoint_data = json.load(f)

        self.documents = {doc_data['doc_id']: Document(**doc_data) for doc_data in checkpoint_data['documents']}
        self.company_index = checkpoint_data['company_index']
        self.table_index = checkpoint_data['table_index']
        
        logger.success(f"Successfully loaded {len(self.documents)} documents and indices from checkpoints.")

    def search(self, query: str, k: int = 5, company_filter: Optional[str] = None, table_filter: Optional[str] = None) -> List[Document]:
        """
        Performs a hybrid search (metadata filtering + vector search).
        """

        query_embedding = self.embedding_model.encode([query])
        selected_ids = set()

        if company_filter and company_filter in self.company_index:
            selected_ids = set(self.company_index[company_filter])
            
        if table_filter and table_filter in self.table_index:
            valid_ids = set(self.table_index[table_filter])
            if selected_ids:
                selected_ids.intersection_update(valid_ids)
            else:
                selected_ids = valid_ids

        if selected_ids:
            logger.debug(f"Performing search with selected_ids: {selected_ids}")
            ids_to_search = np.array(list(selected_ids), dtype='int64')
            id_selector = faiss.IDSelectorArray(ids_to_search)
            distances, indices = self.faiss_index.search(
                query_embedding,
                k,
                params=faiss.SearchParametersIVF(sel=id_selector)
            )
        else:
            logger.debug("No filters applied; searching across all documents.")
            distances, indices = self.faiss_index.search(query_embedding, k)

        
        logger.success(f"FAISS search results: distances: {distances}, indices: {indices}")

        results = []
        if len(indices) > 0:
            for doc_id in indices[0]:
                if doc_id != -1: # FAISS returns -1 for no result
                    results.append(self.documents[doc_id])
        return results
