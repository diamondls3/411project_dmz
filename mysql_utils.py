import pymysql
import pandas as pd

DB_CONFIG = {
  'host': 'localhost',
  'user': 'root',
  'password': 'test_root',
  'db': 'academicworld',
  'charset':'utf8mb4', 
  'cursorclass':pymysql.cursors.DictCursor
}

def query_mysql(query, params=None):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        return result
    finally:
        connection.close()

def get_keyword_names():
    query = """
            SELECT distinct keyword.name as name
            FROM keyword 
            ORDER BY name 
          """
    return query_mysql(query)

def get_top_researchers_by_KRC(keyword):
    query = """
            SELECT  trim(faculty.name) as professor,
                    university.name as university,
                    sum(publication.num_citations) as cit_sum,
                    count(distinct publication.id) as pub_cnt,
                    sum(publication.num_citations * publication_keyword.score) AS KRC
            FROM faculty
            JOIN faculty_publication 
            JOIN publication 
            JOIN publication_keyword 
            JOIN keyword 
            JOIN university
            WHERE faculty.id = faculty_publication.faculty_id
                AND publication.id = faculty_publication.publication_id
                AND publication_keyword.publication_id = publication.id 
                AND keyword.id = publication_keyword.keyword_id
                AND university.id = faculty.university_id
                AND keyword.name = %s
            GROUP BY trim(faculty.name), university.name
            ORDER BY KRC DESC
            LIMIT 10
        """
    return query_mysql(query, (keyword,))

def get_professor_names():
    query = """
            SELECT  distinct
                    trim(faculty.name) as name
            FROM faculty
            JOIN faculty_keyword
            JOIN keyword 
            WHERE faculty.id = faculty_keyword.faculty_id
                  AND keyword.id = faculty_keyword.keyword_id 
          ORDER BY name 
          """
    return query_mysql(query)

def get_professor_research_interest(professor):
    query = """
            with top3_research_interest as (
                    select  faculty_id, 
                            faculty,
                            research_interest_id, 
                            research_interest, 
                            faculty_interest_score,
                            sum(faculty_interest_score) over (partition by faculty_id) as total_research_interest_score,
                            faculty_interest_score/sum(faculty_interest_score) over (partition by faculty_id) as research_interest_percentage,
                            rnk
                    from (  SELECT faculty.id as faculty_id, 
                                trim(faculty.name) as faculty,
                                keyword.id as research_interest_id, 
                                keyword.name as research_interest, 
                                score as faculty_interest_score,
                                rank()over(partition by faculty.id order by score desc) as rnk
                            FROM faculty
                            JOIN faculty_keyword
                            JOIN keyword 
                            WHERE keyword.id = faculty_keyword.keyword_id 
                                AND faculty.id = faculty_keyword.faculty_id
                        ) a
                    where rnk <= 3 and faculty = %s
            )
            select faculty, research_interest, rnk, 
                faculty_interest_score, 
                publication.title as publication_title,
                publication.year,
                publication.venue,
                substring(publication.venue, 1, 30) as venue_short,
                keyword.name as publication_keyword,
                publication_keyword.score as publication_keyword_score,
                publication_keyword.score/sum(publication_keyword.score) over (partition by research_interest) * faculty_interest_score as score
            from top3_research_interest
            JOIN faculty_publication 
            JOIN publication 
            JOIN publication_keyword 
            JOIN keyword 
            WHERE top3_research_interest.faculty_id = faculty_publication.faculty_id
                AND publication.id = faculty_publication.publication_id
                AND publication_keyword.publication_id = publication.id 
                AND keyword.id = publication_keyword.keyword_id
                AND top3_research_interest.research_interest_id = keyword.id
        """
    return query_mysql(query,(professor,))


def get_professor_publications(professor):
    query = """
            WITH top_keyword as
	 (  SELECT  publication.id as publication_id,
			    max(score) as max_score
		FROM faculty
		JOIN faculty_publication 
		JOIN publication 
		JOIN publication_keyword
        JOIN keyword 
        WHERE faculty.id = faculty_publication.faculty_id
			  AND publication.id = faculty_publication.publication_id
			  AND publication_keyword.publication_id = publication.id 
			  AND keyword.id = publication_keyword.keyword_id
			  AND trim(faculty.name) = %s
		group by publication.id
		) 
SELECT  trim(faculty.name) as professor,
	    publication.id as publication_id,
	    publication.title as publications, 
	    publication.num_citations,
	    keyword.name as most_related_publication_keyword,
	    score as keyword_score
FROM faculty
JOIN faculty_publication 
JOIN publication 
JOIN publication_keyword
JOIN top_keyword
JOIN keyword 
WHERE faculty.id = faculty_publication.faculty_id
	  AND publication.id = faculty_publication.publication_id
	  AND publication_keyword.publication_id = publication.id 
      AND top_keyword.publication_id = publication_keyword.publication_id
      AND top_keyword.max_score = publication_keyword.score
	  AND keyword.id = publication_keyword.keyword_id
          """
    return query_mysql(query,(professor))