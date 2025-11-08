-- SQL pentru crearea tabelului predictions în Supabase
-- Copiați și executați acest script în Supabase SQL Editor

-- Creare tabel predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    predicted_class TEXT NOT NULL CHECK (predicted_class IN ('human', 'robot')),
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Index pentru căutări rapide după timestamp
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp DESC);

-- Index pentru căutări după clasă
CREATE INDEX IF NOT EXISTS idx_predictions_class ON predictions(predicted_class);

-- Comentarii pentru documentație
COMMENT ON TABLE predictions IS 'Stochează predicțiile făcute de modelul CNN pentru clasificarea imagini robot vs human';
COMMENT ON COLUMN predictions.filename IS 'Numele fișierului imaginii încărcate';
COMMENT ON COLUMN predictions.predicted_class IS 'Clasa prezisă: human sau robot';
COMMENT ON COLUMN predictions.confidence IS 'Nivelul de încredere al predicției (0-1)';
COMMENT ON COLUMN predictions.timestamp IS 'Data și ora predicției';

-- Verificare tabel creat
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'predictions'
ORDER BY ordinal_position;

-- Afișare primele înregistrări (după ce adăugați date)
-- SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;
