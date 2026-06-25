from app.multimodal_runtime.file_detector.detector import FileTypeDetector
from app.multimodal_runtime.format_analyzer.analyzer import FormatAnalyzer
from app.multimodal_runtime.extraction_engine.engine import ExtractionEngine
from app.multimodal_runtime.graph_node.node import MultimodalGraphNode

class MultimodalRuntime:
    def process(self, file_path):
        detector = FileTypeDetector()
        file_type = detector.detect(file_path)

        analyzer = FormatAnalyzer()
        steps = analyzer.analyze(file_type)

        extractor = ExtractionEngine()
        content = extractor.extract(file_type, file_path)

        node = MultimodalGraphNode(file_type, content)

        return node.to_graph()
