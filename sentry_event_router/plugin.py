"""
sentry.plugins.sentry_event_router.models
"""

from __future__ import absolute_import

from django.conf import settings
from sentry.plugins import Plugin
from sentry.models import Project

from socket import gethostname
import requests

import sentry_event_router

logger = logging.getLogger(__name__)


class SentryEventRouter(Plugin):
    title = "Event Router"
    conf_key = "event-router"
    conf_title = "Event Router"
    slug = "event-router"
    version = sentry_event_router.VERSION

    author = "Kieran Broekhoven"

    project_default_enabled = False
    project_conf_form = None
    subject_prefix = settings.EMAIL_SUBJECT_PREFIX

    def node_router(self, project_id, helper, request):
        project_id_origin = project_id

        proj_data = request.body
        content_encoding = request.META.get('HTTP_CONTENT_ENCODING', '')

        if isinstance(proj_data, basestring):
            if content_encoding == 'gzip':
                proj_data = helper.decompress_gzip(proj_data)
            elif content_encoding == 'deflate':
                proj_data = helper.decompress_deflate(proj_data)
            elif not data.startswith('{'):
                proj_data = helper.decode_and_decompress_data(proj_data)
            proj_data = helper.safely_load_json_string(proj_data)

        node_name = proj_data.get('tags', {}).get('node_name', None)
        if not node_name:
            return project_id

        original_project = Project.objects.get_from_cache(id=project_id)

        new_proj_data = requests.get("http://%s/api/0/" % gethostname() +
                                     "projects/cpr/%s/" % node_name, auth=(
                                     "d0b15acbe4fd4cb5bfeb14008dbcabe2", ''))

        if new_proj_data.status_code == 200: # Project for this node exists
            logger.info("Node project already exists")
        elif new_proj_data.status_code == 404: # Create new project for node
            logger.info("Creating new node project")
            new_proj_data = requests.post("http://%s/api/0/" % gethostname() +
                                          "teams/cpr/%s/projects/" %
                                          original_project.team.name,
                                          data={"name": node_name}, auth=(
                                          "d0b15acbe4fd4cb5bfeb14008dbcabe2",
                                          ''))
        code = new_proj_data.status_code
        if code == 201 or code == 200:
            project_id = new_proj_data.json().get("id", project_id)
        else:
            logger.error("Failed to reroute event. Response: %s. Request: %s" %
                   (code, original_project.team.name))

        return project_id

    def dispatch(self, project, helper, request):
        project_id = self.node_router(project.id, helper, request)

        helper.context.project_id = str(project_id)

