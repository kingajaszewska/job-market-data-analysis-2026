-- 1. Data-quality overview
SELECT
    record_quality,
    COUNT(*) AS offers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM job_offers
GROUP BY record_quality
ORDER BY offers DESC;

-- 2. Main job families after category normalization
SELECT
    category_group,
    COUNT(*) AS offers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM job_offers
GROUP BY category_group
ORDER BY offers DESC;

-- 3. Availability of graduate-friendly positions
SELECT
    seniority_group,
    COUNT(*) AS offers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM job_offers
GROUP BY seniority_group
ORDER BY offers DESC;

-- 4. Work modes, with missing information kept visible
SELECT
    work_mode_group,
    COUNT(*) AS offers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM job_offers
GROUP BY work_mode_group
ORDER BY offers DESC;

-- 5. Most frequently mentioned tools
SELECT
    tool,
    COUNT(DISTINCT offer_id) AS offers,
    ROUND(100.0 * COUNT(DISTINCT offer_id) / (SELECT COUNT(*) FROM job_offers), 1) AS share_of_all_offers_pct
FROM offer_tools
GROUP BY tool
ORDER BY offers DESC, tool;

-- 6. Source concentration by recruitment portal
SELECT
    portal,
    COUNT(*) AS offers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct,
    DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS portal_rank
FROM job_offers
GROUP BY portal
ORDER BY offers DESC, portal;

-- 7. Verification status by portal
SELECT
    portal,
    COUNT(*) AS collected_offers,
    SUM(CASE WHEN record_quality = 'Verified' THEN 1 ELSE 0 END) AS verified_offers,
    ROUND(
        100.0 * SUM(CASE WHEN record_quality = 'Verified' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS verified_share_pct
FROM job_offers
GROUP BY portal
ORDER BY collected_offers DESC;

-- 8. Job family and work-mode cross-tab for records with known work mode
SELECT
    category_group,
    SUM(CASE WHEN work_mode_group = 'Hybrid' THEN 1 ELSE 0 END) AS hybrid,
    SUM(CASE WHEN work_mode_group = 'On-site' THEN 1 ELSE 0 END) AS on_site,
    SUM(CASE WHEN work_mode_group = 'Remote' THEN 1 ELSE 0 END) AS remote,
    SUM(CASE WHEN work_mode_group = 'Mixed / flexible' THEN 1 ELSE 0 END) AS mixed_flexible
FROM job_offers
WHERE work_mode_group <> 'Unknown'
GROUP BY category_group
ORDER BY category_group;

-- 9. Salary transparency. Salary levels are not compared because currencies,
-- contract types, and time units are not consistent across the source records.
SELECT
    salary_disclosed,
    COUNT(*) AS offers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM job_offers
GROUP BY salary_disclosed
ORDER BY offers DESC;

-- 10. Categories with the highest number of verified records
WITH category_quality AS (
    SELECT
        category_group,
        COUNT(*) AS collected_offers,
        SUM(CASE WHEN record_quality = 'Verified' THEN 1 ELSE 0 END) AS verified_offers
    FROM job_offers
    GROUP BY category_group
)
SELECT
    category_group,
    collected_offers,
    verified_offers,
    ROUND(100.0 * verified_offers / collected_offers, 1) AS verified_share_pct,
    DENSE_RANK() OVER (ORDER BY verified_offers DESC) AS verified_rank
FROM category_quality
ORDER BY verified_rank, category_group;
