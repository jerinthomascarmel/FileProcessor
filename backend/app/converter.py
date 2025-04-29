from docling.document_converter import DocumentConverter

class Converter:
    def __init__(self):
        self.converter = DocumentConverter()

    

    def convert_docx_to_json(self, source_path):
        result = self.converter.convert(source_path)
        docling_json = result.document.export_to_dict()
        return docling_json

    def convert_docx_to_markdown(self, docx_path: str) -> str:
        result = self.converter.convert(docx_path)
        markdown_content = result.document.export_to_markdown()
        return markdown_content
