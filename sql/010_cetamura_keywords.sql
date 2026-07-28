BEGIN TRANSACTION;

UPDATE objects
SET keywords =
    CASE
        WHEN keywords IS NULL OR TRIM(keywords) = ''
        THEN 'Cetamura del Chianti Site|Italy excavations|archaeological digs'
        ELSE keywords || '|Cetamura del Chianti Site|Italy excavations|archaeological digs'
    END
WHERE source_collection IN (
    'fsu_cetamura',
    'fsu_cetamuraphotos',
    'fsu_cetamuraExcavations_trenchPhotos',
    'fsu_cetamuraExcavations_maps'
);

COMMIT;