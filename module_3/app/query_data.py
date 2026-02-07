QUERY_1 = """
SELECT COUNT(*) AS count_fall_2026
FROM applicantData
WHERE term = 'Fall 2026';
"""

QUERY_2 = """
SELECT ROUND(
    100.0 * SUM(
        CASE
            WHEN us_or_international IS NOT NULL
             AND us_or_international NOT ILIKE 'American'
             AND us_or_international NOT ILIKE 'Other'
            THEN 1
            ELSE 0
        END
    ) / NULLIF(COUNT(*), 0),
    2
) AS pct_international
FROM applicantData;
"""

QUERY_3_GPA = """
SELECT AVG(gpa) AS avg_gpa
FROM applicantData
WHERE gpa IS NOT NULL;
"""

QUERY_3_GRE = """
SELECT AVG(gre) AS avg_gre
FROM applicantData
WHERE gre IS NOT NULL;
"""

QUERY_3_GRE_V = """
SELECT AVG(gre_v) AS avg_gre_v
FROM applicantData
WHERE gre_v IS NOT NULL;
"""

QUERY_3_GRE_AW = """
SELECT AVG(gre_aw) AS avg_gre_aw
FROM applicantData
WHERE gre_aw IS NOT NULL;
"""

QUERY_4 = """
SELECT AVG(gpa) AS avg_gpa_american_fall_2026
FROM applicantData
WHERE term = 'Fall 2026'
  AND us_or_international ILIKE 'American'
  AND gpa IS NOT NULL;
"""

QUERY_5 = """
SELECT ROUND(
    100.0 * SUM(CASE WHEN status ILIKE 'Accepted' THEN 1 ELSE 0 END)
    / NULLIF(COUNT(*), 0),
    2
) AS pct_accepted_fall_2026
FROM applicantData
WHERE term = 'Fall 2026';
"""

QUERY_6 = """
SELECT AVG(gpa) AS avg_gpa_fall_2026_accepted
FROM applicantData
WHERE term = 'Fall 2026'
  AND status ILIKE 'Accepted'
  AND gpa IS NOT NULL;
"""

QUERY_7 = """
SELECT COUNT(*) AS count_jhu_ms_cs
FROM applicantData
WHERE degree ILIKE 'Masters%'
  AND program ILIKE '%Computer Science%'
  AND (
      program ILIKE '%Johns Hopkins%'
      OR program ILIKE '%JHU%'
  );
"""

QUERY_7a = """
SELECT COUNT(*) AS count_jhu_ms_cs_llm
FROM applicantData
WHERE degree ILIKE 'Masters%'
  AND llm_generated_program ILIKE '%Computer Science%'
  AND (
      llm_generated_university ILIKE '%Johns Hopkins%'
      OR llm_generated_university ILIKE '%JHU%'
  );
"""

QUERY_8 = """
SELECT COUNT(*) AS count_cs_phd_2026_acceptances_schools
FROM applicantData
WHERE term ILIKE '%2026%'
  AND status ILIKE 'Accepted'
  AND degree ILIKE 'PhD%'
  AND program ILIKE '%Computer Science%'
  AND (
      program ILIKE '%Georgetown University%'
      OR program ILIKE '%MIT%'
      OR program ILIKE '%Massachusetts Institute of Technology%'
      OR program ILIKE '%Stanford University%'
      OR program ILIKE '%Carnegie Mellon University%'
  );
"""

QUERY_8a = """
SELECT COUNT(*) AS count_cs_phd_2026_acceptances_schools_llm
FROM applicantData
WHERE term ILIKE '%2026%'
  AND status ILIKE 'Accepted'
  AND degree ILIKE 'PhD%'
  AND llm_generated_program ILIKE '%Computer Science%'
  AND (
      llm_generated_university ILIKE '%Georgetown University%'
      OR llm_generated_university ILIKE '%MIT%'
      OR llm_generated_university ILIKE '%Massachusetts Institute of Technology%'
      OR llm_generated_university ILIKE '%Stanford University%'
      OR llm_generated_university ILIKE '%Carnegie Mellon University%'
  );
"""

QUERY_9 = """
SELECT COUNT(*) AS count_engineering_rejected
FROM applicantData
WHERE term ILIKE '%2026%'
  AND status ILIKE 'Rejected'
;
"""

QUERY_10 = """
SELECT ROUND(
    100.0 * SUM(
        CASE 
            WHEN status ILIKE 'Rejected'
             AND us_or_international NOT ILIKE 'International'
            THEN 1
            ELSE 0
        END
    ) / NULLIF(COUNT(*), 0),
    2
) AS pct_international_rejected_fall_2026
FROM applicantData
WHERE term = 'Fall 2026';
"""

import psycopg

DB_NAME = "studentCourses"
DB_USER = "postgres"

QUERIES = [
    ("1. Number of applications for Fall 2026", QUERY_1),
    ("2. Percentage of international students (not American/Other)", QUERY_2),
    ("3. Average GPA", QUERY_3_GPA),
    ("3. Average GRE", QUERY_3_GRE),
    ("3. Average GRE V", QUERY_3_GRE_V),
    ("3. Average GRE AW", QUERY_3_GRE_AW),
    ("4. Average GPA of American students in Fall 2026)", QUERY_4),
    ("5. Percent of Fall 2026 acceptances", QUERY_5),
    ("6. Average GPA of applicants who applied for Fall 2026", QUERY_6),
    ("7. Number of applicants who applied to JHU for MS Computer Science degrees", QUERY_7),
    ("7a. Number of applicants who applied to JHU for MS Computer Science degrees (LLM)", QUERY_7a),
    ("8. Number of 2026 acceptances for CS PhD at Georgetown, MIT, Stanford, Carnegie Mellon", QUERY_8),
    ("8a. Number of 2026 acceptances for CS PhD at Georgetown, MIT, Stanford, Carnegie Mellon (LLM)", QUERY_8a),
    ("9. Number of rejected engineering applicants for Fall 2026", QUERY_9),
    ("10. Percent of rejected international engineering applicants for Fall 2026", QUERY_10)
]

if __name__ == "__main__":
    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
    ) as connection:
        with connection.cursor() as cur:
            for label, query in QUERIES:
                cur.execute(query)
                result = cur.fetchone()
                print(f"{label}: {result[0] if result else None}")
