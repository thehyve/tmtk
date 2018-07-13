import json
import os

import click
import numpy as np
import pandas as pd
from tmtk import arborist


def arborist_to_tree_template(tree_input, output_dir='.', no_metadata=False):
    """
    Create an Excel file containing the tree structure template
    based on the JSON of an Arborist tree.
    :param tree_input: An exported treefile or an Arborist tree URL
    :param output_dir: The folder where the output will be written
    :param no_metadata: if True metadata will be ignored
    """
    json_tree, study_name = _interpret_input(tree_input)
    tree = _ArboristToTemplate(json_tree, study_name, output_dir, no_metadata)
    tree.transform_to_template()
    print("Processing complete")


def _interpret_input(tree_input):
    if tree_input.startswith('http'):
        json_tree = _get_json_tree_from_url(tree_input)
        study_name = _get_study_name_from_url(tree_input)
    else:
        json_tree = _get_json_tree_from_file(tree_input)
        study_name = os.path.splitext(os.path.basename(tree_input))[0]
    print('Inferred study name: {}'.format(study_name))
    return json_tree, study_name


def _get_study_name_from_url(tree_input_url):
    # Name of study is the URL part after "trees"
    parts = tree_input_url.split('/')
    trees_index = parts.index('trees')
    study_name = parts[trees_index+1]
    return study_name


def _get_json_tree_from_file(tree_input):
    check = click.Path(exists=True, dir_okay=False, readable=True)
    check(tree_input)
    return _read_json_file(tree_input)


def _get_json_tree_from_url(tree_input_url):
    username = input("Arborist username: ")
    json_string = arborist.get_json_from_baas(tree_input_url, username=username)
    return json.loads(json_string)


def _read_json_file(file_path):
    with open(file_path, 'r') as contents:
        return json.load(contents)


class _ArboristToTemplate:

    def __init__(self, json_tree, study_name, output_dir='.', no_metadata=False):
        self.raw_tree = json_tree
        self.study_name = study_name
        self.output_path = os.path.join(output_dir, self.study_name+'_as_template.xlsx')
        self.skip_metadata = no_metadata

        self.df = pd.DataFrame()

    def transform_to_template(self):
        self.add_root_to_json_tree()
        self.loop_through_nodes(self.raw_tree)
        self.add_missing_metadata_columns()
        self.order_columns()
        self.add_mandatory_columns()

        writer = pd.ExcelWriter(self.output_path)
        self.df.to_excel(writer, sheet_name='Tree structure template', index=False)
        writer.save()
        print("Template written at: {}".format(self.output_path))

    def add_root_to_json_tree(self):
        full_tree = {'id': 'root', 'text': self.study_name, 'data': {}, 'children': self.raw_tree}
        self.raw_tree = full_tree

    def add_mandatory_columns(self):
        self.df.insert(loc=0, column='Column number', value=np.nan)
        self.df.insert(loc=0, column='Sheet name/File name', value=np.nan)
        self.df.insert(loc=0, column='tranSMART data type', value='Low-dimensional')

    def order_columns(self):
        level_order = ['Level {}', 'Level {} metadata tag', 'Level {} metadata value']
        max_level = max(
            [int(col.split()[1]) for col in self.df.columns if col.startswith('Level') and not 'metadata' in col])
        ordered_cols = [col.format(i) for i in range(1, max_level + 1) for col in level_order]
        self.df = self.df.reindex(ordered_cols, axis=1)

    def add_missing_metadata_columns(self):
        levels = {col.split()[1] for col in self.df.columns}
        for level in levels:
            if 'Level {} metadata tag'.format(level) not in self.df.columns:
                self.df['Level {} metadata tag'.format(level)] = np.nan
            if 'Level {} metadata value'.format(level) not in self.df.columns:
                self.df['Level {} metadata value'.format(level)] = np.nan

    def add_metadata_to_df(self, metadata, row_index, level):
        for item in metadata:
            tag = item[0]
            value = item[1][0]
            self.df.loc[row_index, 'Level {} metadata tag'.format(level)] = tag
            self.df.loc[row_index, 'Level {} metadata value'.format(level)] = value
            row_index += 1

    def determine_row_index(self, last_row_index, cols_equal_or_higher_level, last_regular_node_row_index):
        """Determine the row index on which the current node should be inserted."""
        # The df is still empty
        if last_row_index is None:
            row_index = 0
        # If all >= levels on this row are empty, add node on the same row
        elif all(self.df.loc[last_row_index, cols_equal_or_higher_level].isnull()):
            row_index = last_regular_node_row_index
        # Otherwise insert node on a new row
        else:
            row_index = last_row_index + 1
        return row_index

    def insert_node_data_into_df(self, node, depth):
        last_row_index = max(self.df.apply(pd.Series.last_valid_index), default=None)
        regular_node_cols = [col for col in self.df.columns if 'metadata' not in col]
        last_regular_node_row_index = max(self.df[regular_node_cols].apply(pd.Series.last_valid_index), default=None)
        cols_equal_or_higher_level = [col for col in self.df.columns if int(col.split()[1]) >= depth]

        row_index = self.determine_row_index(last_row_index, cols_equal_or_higher_level, last_regular_node_row_index)
        self.df.loc[row_index, 'Level {}'.format(depth)] = node['text']

        if 'metadata' in node:
            self.add_metadata_to_df(node['metadata'], row_index, depth)

    def add_metadata_to_node_level(self, node):
        """Add metadata to actual node instead of it being a child node"""
        if any([child_node['text'] == 'Tags' for child_node in node['children']]):
            node['metadata'] = [child['data']['tags'] for child in node['children'] if child['text'] == 'Tags'][0]
            # Sort tags by weight
            node['metadata'] = sorted(node['metadata'].items(), key=lambda kv: int(kv[1][1]))

    def loop_through_nodes(self, node, depth=1):
        if not self.skip_metadata:
            self.add_metadata_to_node_level(node)
        # Skip tag nodes and categorical values
        if node['text'] in ['Tags', 'SUBJ_ID'] or node.get('type') == 'alpha':
            return
        self.insert_node_data_into_df(node, depth)

        for child_node in node['children']:
            self.loop_through_nodes(child_node, depth+1)


@click.command()
@click.argument('tree_input')
@click.option('-o', '--output_dir', type=click.Path(exists=False, file_okay=False, writable=True), default='.',
              help='Directory where the output should be written to')
@click.option('--no-metadata', is_flag=True, default=False, show_default=True,
              help='Ignore all metadata in the tree file')
def _main(tree_input, output_dir, no_metadata):
    """1. Either a path to a treefile or an Arborist URL of a tree."""
    arborist_to_tree_template(tree_input, output_dir, no_metadata)


if __name__ == "__main__":
    _main()
