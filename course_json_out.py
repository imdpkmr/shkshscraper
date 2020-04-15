import sys
import json_out
from database import DBQueries

course_table_query = f"CREATE TABLE courses(" \
                       f"name_of_the_university VARCHAR(400)," \
                       f"level VARCHAR(400)," \
                       f"stream VARCHAR(400)," \
                       f"degree VARCHAR(400)," \
                       f"specialization VARCHAR(400)," \
                       f"course_name VARCHAR(400)," \
                       f"`department\school` VARCHAR(400)," \
                       f"mode VARCHAR(400)," \
                       f"duration VARCHAR(400)," \
                       f"duration_type VARCHAR(400)," \
                       f"tuition_fees VARCHAR(400)," \
                       f"tuition_fees_currency VARCHAR(400)," \
                       f"tuition_fees_duration_type VARCHAR(400)," \
                       f"application_fee VARCHAR(400)," \
                       f"application_fee_currency VARCHAR(400)," \
                       f"date_type VARCHAR(400)," \
                       f"season VARCHAR(400)," \
                       f"date VARCHAR(400)" \
                       f")"

if __name__ == "__main__":
    pass
    db = DBQueries()
    rurl_conx = db.connect("Institute")
    rurls_ids = db.get_records(rurl_conx, "select course_id, course_rel_url from url_courses order by course_id limit 5")
    rurl_conx.close()
    for rurl_id in rurls_ids:
        print(rurl_id[0], "->", rurl_id[1])




    ct_conx = db.connect("ShikshaData")
    db._create_table(ct_conx, course_table_query)
    ct_conx.commit()
    ct_conx.close

