import ezdxf

class DWGParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dxf_document = None

    def load_file(self):
        """Load a DWG file using ezdxf."""
        try:
            self.dxf_document = ezdxf.readfile(self.filepath)
        except Exception as e:
            print(f"Error loading file: {e}")

    def extract_layers(self):
        """Extract layers from the loaded DWG file."""
        if self.dxf_document is not None:
            return self.dxf_document.layers
        return None

    def extract_blocks(self):
        """Extract blocks from the loaded DWG file."""
        if self.dxf_document is not None:
            return self.dxf_document.blocks
        return None

    def extract_texts(self):
        """Extract all texts from the loaded DWG file."""
        if self.dxf_document is not None:
            texts = []
            msp = self.dxf_document.modelspace()
            for text in msp.query('TEXT'):  # Ensure you're querying the proper entities
                texts.append(text)
            return texts
        return None

    def extract_dimensions(self):
        """Extract dimensions from the loaded DWG file."""
        if self.dxf_document is not None:
            dimensions = []
            msp = self.dxf_document.modelspace()
            for dim in msp.query('DIMENSION'):
                dimensions.append(dim)
            return dimensions
        return None

    def extract_block_inserts(self):
        """Extract block inserts from the loaded DWG file."""
        if self.dxf_document is not None:
            block_inserts = []
            msp = self.dxf_document.modelspace()
            for insert in msp.query('INSERT'):
                block_inserts.append(insert)
            return block_inserts
        return None
