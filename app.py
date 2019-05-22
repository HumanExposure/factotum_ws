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
md = Markdown(app, extensions=["fenced_code"])


class ApiDoc:
    """A class to parse and hold API docstrings."""

    def __init__(self, func):
        """Parse and hold API docstrings.

        Arguments:
            function: a function holding a doctstring

        Properties:
            summary (str): the API summary
            note (str): additional information regarding the docstring
            verb (str): the REST verb
            uri (str): the API URI
            arguments (dict): a dictionary of arguments and their descriptions
            returns (str): a string describing the REST response
            example_query_string (str): an example query string input
            example_response (str): an example of the REST response
            py (str): an example calling the API with Python
            curl (str): an example calling the API with cURL
            Ruby (str): an example calling the API with Ruby
            R (str): an example calling the API with R

        """
        doc = func.__doc__.splitlines()
        api_i = self._find_i(doc, "API info:")
        arg_i = self._find_i(doc, "Arguments:")
        ret_i = self._find_i(doc, "Returns:")
        exm_i = self._find_i(doc, "Example:")
        self.base_uri = (
            "https://" + app.config["SERVER_NAME"]
            if app.config["SERVER_NAME"]
            else "http://localhost:5000"
        )
        self.summary = doc[0].strip()
        self.note = " ".join(doc[1:api_i]).strip()
        api_dict = self._arg_dict(doc[api_i:arg_i])
        self.verb = api_dict["verb"]
        self.uri = api_dict["uri"]
        self.arguments = self._arg_dict(doc[arg_i:ret_i])
        self.returns = self._body_str(doc[ret_i:exm_i], formatted=True)
        exm_dict = self._arg_dict(doc[exm_i:-2], formatted=True)
        self.example_query_string = exm_dict["query string"]
        self.example_response = exm_dict["response"]
        api_uri = self.base_uri + self.uri + self.example_query_string
        self.py = "\n".join(
            [
                ">>> import requests",
                ">>> r = requests.get('%s')" % api_uri,
                ">>> r.json()",
            ]
        )
        self.curl = "$ curl '%s'" % api_uri
        self.ruby = "\n".join(
            [
                "require 'net/http'",
                "require 'json'",
                "",
                "uri = URI('%s')" % api_uri,
                "response = Net::HTTP.get(uri)",
                "JSON.parse(response)",
            ]
        )
        self.r = "\n".join(
            [
                "library(httr)",
                "",
                "respone <- GET('%s')" % api_uri,
                "content(r, 'parsed')",
            ]
        )

    def _find_i(self, doc, s):
        """Find the first occurence of a string `s` in an array `doc` of strings."""
        try:
            i = next(i for i in range(len(doc)) if s in doc[i])
        except StopIteration:
            i = None
        return i

    def _arg_dict(self, doc, formatted=False):
        """Return a dictionary of arguments from a array of strings `doc`."""
        args = {}
        tab_size = len(doc[0]) - len(doc[0].lstrip())
        i = 1
        while i < len(doc):
            arg = None
            if doc[i]:
                arg, desc = [s.strip() for s in doc[i].split(":")]
            i += 1
            while (
                arg
                and i < len(doc)
                and (not doc[i] or len(doc[i]) - len(doc[i].lstrip()) - tab_size >= 8)
            ):
                if doc[i]:
                    if desc and not formatted:
                        desc += " "
                    desc += (
                        doc[i][tab_size + 8 :] + "\n" if formatted else doc[i].strip()
                    )
                else:
                    desc += "\n"
                i += 1
            if arg:
                args[arg] = desc.rstrip()
        return args

    def _body_str(self, doc, formatted=False):
        """Return a body paragraph of an array `doc` of strings."""
        tab_size = len(doc[0]) - len(doc[0].lstrip())
        body = ""
        for s in doc[1:]:
            if body and not formatted:
                body += " "
            body += s[tab_size + 4 :] + "\n" if formatted else s.strip()
        return body.rstrip()


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


@app.route("/pucs", methods=["GET"])
def puc_lookup():
    """Retrieve a list of PUCs and the number of products associated with a DTXSID.

    API info:
        verb: GET
        uri: /pucs

    Arguments:
        DTXSID???????: a DTXSID where "???????" is a DTXSID number
        level: the level of verbosity (1-3, default is 3)

    Returns:
        Returns a list of json objects populated with values dictated by the level.

    Example:
        query string: ?DTXSID9022528&level=3
        response:
            [
              {
                "description": "lotions and creams primarily for hands and body",
                "general_category": "Personal care",
                "num_products": 1,
                "product_family": "general moisturizing",
                "product_type": "hand/body lotion"
              }
            ]

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


@app.route("/", methods=["GET"])
def home(name=None):
    """Return the webservice index page."""
    puc_docs = [ApiDoc(puc_lookup)]
    docs = {"Product Use Category (PUC)": {"href": "puc", "apis": puc_docs}}

    return render_template("index.html", name=name, docs=docs)
