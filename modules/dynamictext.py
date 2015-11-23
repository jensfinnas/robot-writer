# -*- coding: utf-8 -*-
from jinja2 import Template


class DynamicText(object):
    def __init__(self, template_path, context):
        """ Render a template with a given context (the data passed to the template)
        """
        template = Template(open(template_path).read().decode("utf-8"))
        self.text = template.render(context)

    def as_markdown(self):
        """ Not implemented yet
        """
        pass

    def as_html(self):
        return self.text