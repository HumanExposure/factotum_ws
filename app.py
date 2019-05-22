"""Factotum Web Services.

A Flask based service to provide a RESTful interface to Factotum data.
"""
import re

import flask
from flask import json
from flask import render_template
from flask import request
from flaskext.markdown import Markdown

import settings

app = flask.Flask(__name__)
app.config.from_object(settings.FlaskConfig)


def sql_query(query_str, fetch_size="all"):
    """Get a SQL datastream.

    Arguments:
        `query_str`
            a SQL command expressed as a string
        `fetch_size`
            how many records to get. Can be a number or "all"
    """
    sql = settings.PyMySQLConfig().get_connection()
    try:
        with sql.cursor() as cursor:
            cursor.execute(query_str)
            if fetch_size == "all":
                result = cursor.fetchall()
            elif fetch_size == 1:
                result = cursor.fetchone()
            elif fetch_size > 1:
                result = cursor.fetchmany(size=fetch_size)
            return result
    finally:
        sql.close()


@app.route("/", methods=["GET"])
def home(name=None):
    """Return the webservice index page."""
    return render_template("index.html", name=name)


@app.route("/pucs", methods=["GET"])
def puc_lookup():
    """Retreive a list of PUCs and the number of products associate with a DTXSID.

    Arguments:
        `DTXSID???????`
            a DTXSID where `???????` is a DTXSID number
        `level = {1,2,default=3}`
            the level of verbosity.
    Returns:
        A json object populated with values dictated by the level.
        1) general_category, num_products
        2) general_category, product_family, num_products
        3) general_category, product_family, product_type, description, num_products

    """
    try:
        dtxsid = next(key for key in request.args.keys() if key[:6] == "DTXSID")
    except StopIteration:
        dtxsid = None
    level = request.args.get("level")
    if level == "1":
        selects = ", ".join(["dashboard_puc.gen_cat"])
    elif level == "2":
        selects = ", ".join(["dashboard_puc.gen_cat", "dashboard_puc.prod_fam"])
    else:
        selects = ", ".join(
            [
                "dashboard_puc.gen_cat",
                "dashboard_puc.prod_fam",
                "dashboard_puc.prod_type",
                "dashboard_puc.description",
            ]
        )
    query_str = re.sub(
        r"\s+",
        " ",
        """
        SELECT
               %s,
               COUNT(DISTINCT dashboard_producttopuc.product_id) as num_prod
        FROM   dashboard_dsstoxlookup
               INNER JOIN dashboard_rawchem
                       ON ( dashboard_dsstoxlookup.id = dashboard_rawchem.dsstox_id )
               INNER JOIN dashboard_extractedtext
                       ON ( dashboard_rawchem.extracted_text_id =
                            dashboard_extractedtext.data_document_id
                          )
               INNER JOIN dashboard_datadocument
                       ON ( dashboard_extractedtext.data_document_id =
                            dashboard_datadocument.id )
               INNER JOIN dashboard_productdocument
                       ON ( dashboard_datadocument.id =
                            dashboard_productdocument.document_id )
               INNER JOIN dashboard_product
                       ON ( dashboard_productdocument.product_id = dashboard_product.id
                          )
               INNER JOIN dashboard_producttopuc
                       ON ( dashboard_product.id = dashboard_producttopuc.product_id )
               INNER JOIN dashboard_puc
                       ON ( dashboard_producttopuc.puc_id = dashboard_puc.id )
        WHERE  sid = '%s'
        GROUP BY %s
    """
        % (selects, dtxsid, selects),
    )
    result_tuple = sql_query(query_str)
    result_list = []
    for result in result_tuple:
        if level == "1":
            result_list.append(
                {"general_category": result[0], "num_products": result[1]}
            )
        elif level == "2":
            result_list.append(
                {
                    "general_category": result[0],
                    "product_family": result[1],
                    "num_products": result[2],
                }
            )
        else:
            result_list.append(
                {
                    "general_category": result[0],
                    "product_family": result[1],
                    "product_type": result[2],
                    "description": result[3],
                    "num_products": result[4],
                }
            )
    return json.jsonify(result_list)
