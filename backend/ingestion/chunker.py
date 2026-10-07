import re
import uuid

class MarkdownChunker:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        # Approximating tokens by characters (1 token ~ 4 chars)
        self.max_chars = chunk_size * 4
        self.overlap_chars = chunk_overlap * 4

    def split_text(self, text: str, source_path: str) -> list[dict]:
        lines = text.split("\n")
        chunks = []
        
        current_heading = "General"
        current_buffer = []
        current_len = 0

        for line in lines:
            if line.startswith("#"):
                # Heading line found, update heading context
                heading_text = line.lstrip("#").strip()
                if heading_text:
                    current_heading = heading_text

            line_len = len(line) + 1 # include newline
            if current_len + line_len > self.max_chars and current_buffer:
                # Flush current buffer to chunk
                chunk_text = "\n".join(current_buffer).strip()
                if chunk_text:
                    chunks.append({
                        "chunk_id": str(uuid.uuid4()),
                        "source_path": source_path,
                        "heading": current_heading,
                        "text": chunk_text
                    })
                
                # Keep overlap from buffer
                overlap_buffer = []
                overlap_len = 0
                for prev_line in reversed(current_buffer):
                    if overlap_len + len(prev_line) <= self.overlap_chars:
                        overlap_buffer.insert(0, prev_line)
                        overlap_len += len(prev_line)
                    else:
                        break
                current_buffer = overlap_buffer
                current_len = overlap_len

            current_buffer.append(line)
            current_len += line_len

        # Flush final remaining buffer
        if current_buffer:
            chunk_text = "\n".join(current_buffer).strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "source_path": source_path,
                    "heading": current_heading,
                    "text": chunk_text
                })

        return chunks
