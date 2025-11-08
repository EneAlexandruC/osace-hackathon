-- SQL pentru crearea tabelului classification în Supabase
-- Copiați și executați acest script în Supabase SQL Editor

-- Creare tabel classification
CREATE TABLE IF NOT EXISTS classification (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    predicted_class TEXT NOT NULL CHECK (predicted_class IN ('human', 'robot')),
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pentru căutări rapide după created_at
CREATE INDEX IF NOT EXISTS idx_classification_created_at ON classification(created_at DESC);

-- Index pentru căutări după clasă
CREATE INDEX IF NOT EXISTS idx_classification_class ON classification(predicted_class);

-- Comentarii pentru documentație
COMMENT ON TABLE classification IS 'Stochează predicțiile făcute de modelul CNN pentru clasificarea imagini robot vs human';
COMMENT ON COLUMN classification.filename IS 'Numele fișierului imaginii încărcate';
COMMENT ON COLUMN classification.predicted_class IS 'Clasa prezisă: human sau robot';
COMMENT ON COLUMN classification.confidence IS 'Nivelul de încredere al predicției (0-1)';
COMMENT ON COLUMN classification.created_at IS 'Data și ora predicției';

-- Verificare tabel creat
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'classification'
ORDER BY ordinal_position;

-- Afișare primele înregistrări (după ce adăugați date)
-- SELECT * FROM classification ORDER BY created_at DESC LIMIT 10;
