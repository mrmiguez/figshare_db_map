BEGIN TRANSACTION;

UPDATE objects
SET keywords =
    CASE
        WHEN keywords IS NULL OR TRIM(keywords) = ''
        THEN 'Cetamura del Chianti Site|Italy excavations|archaeological digs'
        ELSE keywords || '|Cetamura del Chianti Site|Italy excavations|archaeological digs'
    END
WHERE source_collection LIKE '%fsu_cetamura%'
   OR source_collection LIKE '%fsu_cetamuraphotos%'
   OR source_collection LIKE '%fsu_cetamuraExcavations_trenchPhotos%'
   OR source_collection LIKE '%fsu_cetamuraExcavations_maps%';

COMMIT;