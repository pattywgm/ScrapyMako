#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Author: Gaomin Wu / wugm@ruyi.ai
    Time: 2018/8/3 下午2:24
    TODO:
"""
import os
import zipfile
import shutil
from mako.template import Template
import settings


def add_zipfile(source_dir, output_filename):
    f = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            f.write(os.path.join(dirpath, filename))
    f.close()


class BaseTemplate(object):

    def __init__(self, template_name, output_name, output_dir, template_dir="templates"):
        self.template = Template(filename=os.path.join(settings.BASE_DIR, template_dir, template_name), output_encoding="utf-8")
        self.output_filename = os.path.join(output_dir, output_name)

    def render(self, *args, **kwargs):
        with open(self.output_filename, "w+") as f:
            f.write(self.template.render(**kwargs))


def generate_crawl_template(project, rule_fields, output_dir):
    t = BaseTemplate(template_name="scrapy.cfg.tpl", output_name="scrapy.cfg", output_dir=output_dir)
    t.render(**{"project_name": project.name})

    t = BaseTemplate(template_name="template/settings.py.tpl", output_name=project.name + "/settings.py",
                     output_dir=output_dir)
    t.render(**{"project": project})

    t = BaseTemplate(template_name="template/items.py.tpl", output_name=project.name + "/items.py",
                     output_dir=output_dir)
    t.render(**{"rule_fields": rule_fields})

    t = BaseTemplate(template_name="template/spiders/template.py.tpl",
                     output_name=project.name + "/spiders/" + project.name + ".py", output_dir=output_dir)
    t.render(**{"rule_fields": rule_fields, "project": project})

    t = BaseTemplate(template_name="template/pipelines.py.tpl", output_name=project.name + "/pipelines.py",
                     output_dir=output_dir)
    t.render(**{"rule_fields": rule_fields, "project": project})

    t = BaseTemplate(template_name="template/middlewares/useragent_middleware.py.tpl",
                     output_name=project.name + "/middlewares/useragent_middleware.py", output_dir=output_dir)
    t.render()
    t = BaseTemplate(template_name="scripts.py.tpl", output_name="scripts.py", output_dir=output_dir)
    t.render(**{"project": project})


def start_project(project, rule_fields, output_dir=settings.OUTPUT_DIR):
    project_dir = os.path.join(output_dir, project.name)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir)
    sub_dir = os.path.join(project_dir, project.name)
    if os.path.exists(sub_dir):
        shutil.rmtree(sub_dir)
    os.makedirs(sub_dir)
    os.makedirs(os.path.join(sub_dir, "spiders"))
    os.makedirs(os.path.join(sub_dir, "middlewares"))
    open(os.path.join(sub_dir, "__init__.py"), "w").close()
    open(os.path.join(sub_dir, "middlewares", "__init__.py"), "w").close()
    open(os.path.join(sub_dir, "spiders", "__init__.py"), "w").close()
    project['sub_dir'] = sub_dir
    generate_crawl_template(project, rule_fields, project_dir)

    # add_zipfile(os.path.join(output_dir, project["name"]), project_dir + ".zip")
