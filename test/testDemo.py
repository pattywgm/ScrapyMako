#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Author: Gaomin Wu / wugm@ruyi.ai
    Time: 2018/8/3 下午3:57
    TODO:
"""
import os
import unittest
import shutil
from template_render.model import *
from template_render.core import BaseTemplate
from settings import OUTPUT_DIR


def render_template(template_r, temp_name, out_name, out_dir):
    b = BaseTemplate(temp_name, out_name, out_dir)
    b.render(**template_r)


def start_project(project, output_dir=OUTPUT_DIR):
    project_dir = os.path.join(output_dir, project.name)
    if not os.path.exists(project_dir):
        # shutil.rmtree(project_dir)
        os.makedirs(project_dir)
    sub_dir = os.path.join(project_dir, project.name)
    if not os.path.exists(sub_dir):
        # shutil.rmtree(sub_dir)
        os.makedirs(sub_dir)
    if not os.path.exists(os.path.join(sub_dir, "spiders")):
        os.makedirs(os.path.join(sub_dir, "spiders"))
    if not os.path.exists(os.path.join(sub_dir, "middlewares")):
        os.makedirs(os.path.join(sub_dir, "middlewares"))
    open(os.path.join(sub_dir, "__init__.py"), "w").close()
    open(os.path.join(sub_dir, "middlewares", "__init__.py"), "w").close()
    open(os.path.join(sub_dir, "spiders", "__init__.py"), "w").close()
    project.__setattr__('sub_dir', sub_dir)


class TestCase(unittest.TestCase):

    def setUp(self):
        project = {'name': 'TaiHe',
                   'pipelines': ['JsonWriterPipeline'],
                   'download_delay': 1,
                   'image_urls': 'image_srcs',
                   'images': 'images',
                   'spider': Spider({'name': 'taihe',
                                     'result_dir': './result',
                                     'domain': None,
                                     'download_image': False,
                                     'custom_settings': None,
                                     'start_urls': 'http://music.taihe.com/artist'})
                   }
        self.project = Project(project)
        start_project(self.project)

    def test_items(self):
        out_dir = os.path.join(OUTPUT_DIR, self.project.name)
        fields = [Field({'name': 'url'}), Field({'name': 'singerName'})]
        rule = Rule({'item_name': 'TaiHe',
                     'fields': fields})
        render_template({'rule_fields': [rule]}, 'template/items.py.tpl', self.project.name + "/items.py",
                        out_dir)

    def test_pipelines(self):
        out_dir = os.path.join(OUTPUT_DIR, self.project.name)
        render_template({'project': self.project}, 'template/pipelines.py.tpl', self.project.name + "/pipelines.py",
                        out_dir)

    def test_settings(self):
        out_dir = os.path.join(OUTPUT_DIR, self.project.name)
        render_template({'project': self.project}, 'template/settings.py.tpl', self.project.name + "/settings.py",
                        out_dir)

    def test_template(self):
        out_dir = os.path.join(OUTPUT_DIR, self.project.name)
        fields = [Field({'name': 'url', 'path': '//link'}),
                  Field({'name': 'singerName', 'path': '//ul[@class="container"]//a[contains(@href,"artist")]/@title'})]
        rule = Rule({'rule': 'TaiHe',
                     'fields': fields,
                     'item_name': 'TaiHe',
                     'callback_func': 'parse_item'})
        render_template({'rule_fields': [rule], 'project': self.project}, 'template/spiders/template.py.tpl',
                        self.project.name + "/spiders/template.py",
                        out_dir)


if __name__ == '__main__':
    TestCase()
