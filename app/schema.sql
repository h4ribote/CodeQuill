CREATE TABLE IF NOT EXISTS articles (
    id BINARY(16) PRIMARY KEY,
    title TEXT NOT NULL,
    content BLOB NOT NULL,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    view_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS article_tags (
    article_id BINARY(16),
    tag_id INTEGER,
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_articles_title ON articles (title);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags (name);
