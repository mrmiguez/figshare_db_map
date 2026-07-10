.headers on
.mode csv
.once sample.csv

SELECT
    o.*,
    GROUP_CONCAT(
        TRIM(
            COALESCE(a.surname, '') ||
            CASE WHEN a.firstname IS NOT NULL
                 THEN ', ' || a.firstname
                 ELSE ''
            END
        ),
        '; '
    ) AS authors
FROM objects o
LEFT JOIN object_authors oa
    ON o.pid = oa.object_id
LEFT JOIN authors a
    ON oa.author_id = a.id
GROUP BY o.pid
ORDER BY RANDOM()
LIMIT 25;