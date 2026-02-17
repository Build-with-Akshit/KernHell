"""
Semantic Selector Database using ChromaDB.
Stores selectors with semantic meaning for intelligent fallback.
"""
import re
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from typing import List, Dict, Optional
from kernhell.utils import log_info, log_success, log_warning


class SemanticSelector:
    """Vector-based selector matching using ChromaDB"""
    
    def __init__(self, project_root: Path):
        cache_dir = project_root / ".kernhell_cache" / "chromadb"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(cache_dir))
        self.collection = self.client.get_or_create_collection(
            name="selectors",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"  # Fast, lightweight (80MB)
            )
        )
    
    def store_element(self, selector: str, context: Dict[str, str]):
        """
        Store selector with semantic meaning.
        
        Args:
            selector: CSS selector string (e.g., "#login-btn")
            context: Dictionary with semantic info:
                - text: Visible text content
                - role: Element role (button, input, link, etc.)
                - purpose: What the element does (login, submit, etc.)
                - page: Which page it's on
                - aria_label: Accessibility label
        
        Example:
            store_element(
                "#buy-now",
                {
                    'text': 'Buy Now',
                    'role': 'button',
                    'purpose': 'checkout',
                    'page': 'product',
                    'aria_label': 'Complete purchase'
                }
            )
        """
        # Create rich embedding text from context
        embedding_text = " ".join([
            context.get('text', ''),
            context.get('role', ''),
            context.get('purpose', ''),
            context.get('aria_label', ''),
            context.get('placeholder', '')
        ]).strip()
        
        if not embedding_text:
            log_warning(f"Empty context for selector {selector}, skipping")
            return
        
        try:
            # ChromaDB IDs must be safe strings — sanitize selector
            safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', selector)
            
            self.collection.upsert(
                documents=[embedding_text],
                metadatas=[{'selector': selector, **context}],
                ids=[safe_id]
            )
        except Exception as e:
            log_warning(f"Failed to store {selector}: {e}")
    
    def find_similar(self, query: str, n_results: int = 5) -> List[str]:
        """
        Find elements by semantic meaning.
        
        Args:
            query: Natural language description of what you're looking for
            n_results: Number of similar selectors to return
        
        Returns:
            List of CSS selectors ordered by similarity
        
        Example:
            find_similar("button to complete purchase")
            # Returns: ['#buy-now', '.checkout-btn', '[data-action="buy"]', ...]
        """
        try:
            # Guard: don't query empty collection
            if self.collection.count() == 0:
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            if not results['metadatas'] or not results['metadatas'][0]:
                return []
            
            selectors = [meta['selector'] for meta in results['metadatas'][0]]
            log_success(f"Found {len(selectors)} similar selectors for: '{query}'")
            return selectors
        except Exception as e:
            log_warning(f"Semantic search failed: {e}")
            return []
    
    def populate_from_page(self, page_html: str, page_url: str):
        """
        Extract and store all interactive elements from a page.
        
        Args:
            page_html: Full HTML content of the page
            page_url: URL of the page (for context)
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            log_warning("BeautifulSoup not installed, cannot populate from HTML")
            return
        
        soup = BeautifulSoup(page_html, 'html.parser')
        
        # Find all interactive elements
        interactive_tags = ['button', 'a', 'input', 'select', 'textarea']
        elements_stored = 0
        
        for tag in soup.find_all(interactive_tags):
            selector = self._generate_selector(tag)
            if not selector:
                continue
            
            context = {
                'text': tag.get_text(strip=True)[:100],
                'role': tag.name,
                'page': page_url,
                'aria_label': tag.get('aria-label', ''),
                'placeholder': tag.get('placeholder', ''),
                'type': tag.get('type', ''),
                'name': tag.get('name', '')
            }
            
            self.store_element(selector, context)
            elements_stored += 1
        
        log_success(f"Indexed {elements_stored} interactive elements from {page_url}")
    
    def _generate_selector(self, tag) -> Optional[str]:
        """
        Generate best selector for element.
        Priority: id > data-testid > name > class > tag
        """
        # Priority 1: ID (most stable)
        if tag.get('id'):
            return f"#{tag['id']}"
        
        # Priority 2: data-testid (test-specific)
        if tag.get('data-testid'):
            return f"[data-testid='{tag['data-testid']}']"
        
        # Priority 3: name attribute (forms)
        if tag.get('name'):
            return f"[name='{tag['name']}']"
        
        # Priority 4: First class (less stable)
        if tag.get('class') and len(tag['class']) > 0:
            return f".{tag['class'][0]}"
        
        # Priority 5: Tag + type (very generic)
        if tag.get('type'):
            return f"{tag.name}[type='{tag['type']}']"
        
        return None
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored selectors"""
        try:
            count = self.collection.count()
            return {
                'total_selectors': count,
                'collection_name': self.collection.name
            }
        except Exception:
            return {'total_selectors': 0}
