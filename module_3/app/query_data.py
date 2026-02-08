"""
This module contains declarations for all the sql queries,
the structured output to render on the website and to output
to console, and it contains a main declaration to run the
script directly or testing purposes.
"""

import psycopg


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

QUERY_3 = """
SELECT
    /* Round float cast as numeric to two decimal places */
    ROUND(AVG(gpa)::numeric, 2) AS avg_gpa,
    ROUND(AVG(gre)::numeric, 2) AS avg_gre,
    ROUND(AVG(gre_v)::numeric, 2) AS avg_gre_v,
    ROUND(AVG(gre_aw)::numeric, 2) AS avg_gre_aw
FROM applicantData;
"""

QUERY_4 = """
SELECT ROUND(AVG(gpa)::numeric, 2) AS avg_gpa_american_fall_2026
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
SELECT ROUND(AVG(gpa)::numeric, 2) AS avg_gpa_fall_2026_accepted
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

# list of queries
QUERIES = [
    (
        "1. How many entries do you have in your database who have applied for Fall 2026?",
        "Answer: Applicant count: ",
        QUERY_1,
    ),
    ("2. What percentage of entries are from international students (not American or Other) (to two decimal places)?",
     "Answer: Percent International: ",
     QUERY_2),
    ("3. What is the average GPA, GRE, GRE V, and GRE AW of applicants who provide these metrics?",
     "Answer: ",
     QUERY_3),
    ("4. What is their average GPA of American students in Fall 2026?)", "Answer: Average GPA American: ", QUERY_4),
    ("5. What percent of entries for Fall 2026 are Acceptances (to two decimal places)?", "Answer: Acceptance"
                                                                                          " percent: ", QUERY_5),
    ("6. What is the average GPA of applicants who applied for Fall 2026 who are Acceptances?", "Answer: Average"
                                                                                                " GPA Acceptance: ",
     QUERY_6),
    ("7. How many entries are from applicants who applied to JHU for a masters degrees in Computer Science?",
     "Answer: JHU CS Masters Applicants: ", QUERY_7),
    ("7a. Number of applicants who applied to JHU for MS Computer Science degrees (LLM)",
     "Answer: JHU CS Masters Applicants (LLM): ",
     QUERY_7a),
    ("8. How many entries from 2026 are acceptances from applicants who applied to Georgetown University, MIT,"
     " Stanford University, or Carnegie Mellon University for a PhD in Computer Science?",
     "Answer: 2026 Acceptances for CS PhD at Georgetown, Stanford and Carnegie Mellon: ", QUERY_8),
    ("8a. Number of 2026 acceptances for CS PhD at Georgetown, MIT, Stanford, Carnegie Mellon (LLM)",
     "Answer: 2026 Acceptances for CS PhD at Georgetown, Stanford and Carnegie Mellon (LLM): ", QUERY_8a),
    ("9. Number of rejected engineering applicants for Fall 2026", "Answer: Count of rejected Engineering applicants"
                                                                   " for Fall 2026: ", QUERY_9),
    ("10. Percent of rejected international engineering applicants for Fall 2026",
     "Answer: Percent of rejected international engineering applicants for Fall 2026: ", QUERY_10)
]

# connect to database and print query results - used for testing purposes
if __name__ == "__main__":
    with psycopg.connect(
        dbname="studentCourses",
        user="postgres",
    ) as connection:
        with connection.cursor() as cur:
            for label, prefix, query in QUERIES:
                cur.execute(query)
                result = cur.fetchone()
                if result and len(result) > 1:
                    value = f"GPA: {result[0]}, GRE: {result[1]}, GRE V: {result[2]}, GRE AW: {result[3]}"
                else:
                    value = result[0] if result else None
                print(f"{label}: {prefix}{value if result else None}")