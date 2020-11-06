#!/usr/bin/env python

import os
import argparse
import json
import chevron


default_config = {
    'options': [
        {'option': 'file_name',     'type': 'text'},
        {'option': 'title',         'type': 'text'},
        {'option': 'loremipsum',    'type': 'bool'},
        {'option': 'css',           'type': 'bool'},
    ],
    'targets': [
        {'source': 'index.html',    'out': '{{file_name}}.html'},
        {'source': 'style.css',     'out': '{{#css}}style.css{{/css}}'},
    ],
}


def use_template(templates_dir, template_name):
    cur_template_dir = os.path.join(templates_dir, template_name)
    if not os.path.exists(cur_template_dir):
        raise Exception('the specified template "' + template_name 
                + '" does not exist')

    config = default_config
    config_file = os.path.join(cur_template_dir, 'config.json')
    if os.path.isfile(config_file):
        with open(config_file, 'r') as infile:
            config = json.load(infile)
    
    options = {}
    for option in config['options']:
        name = option['option']
        datatype = option['type']
        if datatype == 'text':
            options[name] = input(name + ':')
        elif datatype == 'bool':
            answer = ''
            while answer not in ['y', 'n']:
                answer = input(name + '? (y/n):')
            options[name] = True if answer == 'y' else False 

    for target in config['targets']:
        target_filename = chevron.render(target['out'], options)
        if not target_filename:
            continue
        target_path = os.path.join(os.getcwd(), target_filename)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        source_path = os.path.join(cur_template_dir, target['source'])
        with open(source_path, 'r') as infile:
            with open(target_path, 'w') as outfile:
                translation_args = {
                    'template': infile.read(),
                    'partials_path': cur_template_dir,
                    'partials_ext': 'partial.html',
                    'data': options,
                }
                translated = chevron.render(**translation_args)
                outfile.write(translated)

def new_template(templates_dir, template_name):
    cur_template_dir = os.path.join(templates_dir, template_name)
    if os.path.exists(cur_template_dir):
        raise Exception('the specified template name "' + template_name 
                + '" is already in use')

    os.makedirs(cur_template_dir, exist_ok=True)
    config_file = os.path.join(cur_template_dir, 'config.json')
    with open(config_file, 'w') as outfile:
        json.dump(default_config, outfile, indent=4)





ENVVAR_DIR = 'TEMPL_TEMPLATES_DIR'
templates_dir = os.getenv(ENVVAR_DIR)
if not templates_dir:
    raise Exception('environment variable ' + ENVVAR_DIR 
            + ' must be set to an existing directory')


parser = argparse.ArgumentParser(prog='templ')
subparsers = parser.add_subparsers(dest='command')

use_group = subparsers.add_parser('use', prog='templ use',
        help='instantiate an existing template in the current directory')
use_group.add_argument('template', 
        help='name of an existing template')

new_group = subparsers.add_parser('new', prog='templ new',
        help='create a new blank template')
new_group.add_argument('name', 
        help='name of the new template')

options = parser.parse_args()
if options.command == 'use':
    use_template(templates_dir, options.template)
elif options.command == 'new':
    new_template(templates_dir, options.name)
