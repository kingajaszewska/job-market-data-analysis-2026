PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS offer_tools;
DROP TABLE IF EXISTS job_offers;

CREATE TABLE job_offers (
    offer_id INTEGER PRIMARY KEY,
    portal TEXT NOT NULL,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    seniority_raw TEXT NOT NULL,
    seniority_group TEXT NOT NULL,
    work_mode_raw TEXT NOT NULL,
    work_mode_group TEXT NOT NULL,
    employment_raw TEXT NOT NULL,
    employment_group TEXT NOT NULL,
    category_raw TEXT NOT NULL,
    category_group TEXT NOT NULL,
    tools_raw TEXT NOT NULL,
    salary_raw TEXT NOT NULL,
    salary_disclosed TEXT NOT NULL CHECK (salary_disclosed IN ('Yes', 'No')),
    record_quality TEXT NOT NULL CHECK (
        record_quality IN ('Verified', 'Archived direct record', 'Needs verification')
    ),
    source_url TEXT NOT NULL,
    access_date TEXT NOT NULL,
    tasks_competencies TEXT NOT NULL,
    requirements TEXT NOT NULL,
    fit_notes TEXT NOT NULL,
    status_raw TEXT NOT NULL,
    duplicate_source_url TEXT NOT NULL CHECK (duplicate_source_url IN ('Yes', 'No')),
    duplicate_title_company TEXT NOT NULL CHECK (duplicate_title_company IN ('Yes', 'No'))
);

CREATE TABLE offer_tools (
    offer_id INTEGER NOT NULL,
    tool TEXT NOT NULL,
    PRIMARY KEY (offer_id, tool),
    FOREIGN KEY (offer_id) REFERENCES job_offers (offer_id)
);

CREATE INDEX idx_job_offers_category ON job_offers (category_group);
CREATE INDEX idx_job_offers_work_mode ON job_offers (work_mode_group);
CREATE INDEX idx_job_offers_quality ON job_offers (record_quality);
CREATE INDEX idx_offer_tools_tool ON offer_tools (tool);
