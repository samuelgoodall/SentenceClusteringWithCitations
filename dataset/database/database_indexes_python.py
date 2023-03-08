import sqlite3

# Connect to the database
conn = sqlite3.connect('dataset.db')

# Create indexes
conn.execute('CREATE INDEX paragraph_paper_index ON paragraph(paper_id)')
conn.execute('CREATE INDEX sentence_paragraph_index ON sentence(paragraph_id)')
conn.execute('CREATE UNIQUE INDEX sentence_citation_relation_index ON sentence_citation_relation(sentence_id,citation_id)')

# Commit changes and close the connection
conn.commit()
conn.close()






