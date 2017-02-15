from flask import Response
import json
from lime_endpoints.resources import resource_for

from lime_bootstrap import blueprint as bp

resource = resource_for(
    blueprint=bp,
    routes={
        'bootstrap.info': '/version/',
        }
)


@resource('bootstrap.info')
def get_version_info():
    return Response(json.dumps({'version': 1}),
                    content_type='application/json')


def register_blueprint(app, config=None):
    app.register_blueprint(bp, url_prefix='/lime-bootstrap')
