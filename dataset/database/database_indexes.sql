CREATE INDEX paragraph_paper_index on paragraph(paper_id);
CREATE INDEX sentence_paragraph_index on sentence(paragraph_id);
CREATE UNIQUE INDEX sentence_citation_relation_index on sentence_citation_relation(sentence_id,citation_id);