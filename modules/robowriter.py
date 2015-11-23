# -*- coding: utf-8 -*-

from dynamictext import DynamicText
import sys
import os
from agate import Table, TypeTester


class RoboWriter(object):
    """ Init with a path to a folder with settings, data and text template.
        See examples/unemployment for example.

        RoboWriter.render() writes text.
        RoboWriter.save() saves the text to files.
    """
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.output_folder = folder_path + "/output"

        """ Create a folder for output files if it does not already exist
        """
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        """ Get settings from project folder
        """
        sys.path.insert(0,folder_path)
        from config import SETTINGS
        self.settings = SETTINGS

        self.key = self.settings["data_source"]["key"]

        """ self.data will be an Agate Table object
        """
        self.data = self._get_data()


        if "computed_columns" in self.settings["data_source"]:
            self._add_computed_columns()

        """ comparison_tables will contain rows that can be used for comparison in texts.
            Like neighbours and other municippalities in same county.  
        """
        self.comparison_tables = {} 
        if "compare_categories" in self.settings["data_source"]:
            for category in self.settings["data_source"]["compare_categories"]:
                self._add_comparison_table(category)

        #self.render()
        #self.save("md")

    def _get_data(self):
        if "csv" in self.settings["data_source"]:
            file_path = "%s/%s" % (self.folder_path, self.settings["data_source"]["csv"])
            
            # The csv delimiter can be set as an config option
            delimiter = ","
            if "delimiter" in self.settings["data_source"]:
                delimiter = self.settings["data_source"]["delimiter"]
            
            # Auto-detect column types
            tester = TypeTester(locale='sv_SE',)

            return Table.from_csv(file_path,
                column_types=tester,
                delimiter=delimiter,
                row_names=self.settings["data_source"]["key"])
        else:
            raise ValueError("Could not find any dataset")

    def _add_computed_columns(self):
        computed_columns = self.settings["data_source"]["computed_columns"]
        computations = []
        for column_name, formula in computed_columns.iteritems():
            computations.append((column_name, formula))
        self.data = self.data.compute(computations)

    def _add_comparison_table(self, category):
        self.comparison_tables[category] = {}
        for row in self.data.rows:
            row_name = row[self.key]
            if row_name not in self.comparison_tables:
                self.comparison_tables[row_name] = {}
            _table = self.data.where(lambda r: r[category] == row[category])
            self.comparison_tables[row_name][category] = _table


    def render(self):
        self.texts = []
        for row in self.data.rows:
            row_name = row[self.key]
            template_path = "%s/%s" % (self.folder_path, self.settings["template"])
            
            context = {
                "row": row
            }
            if row_name in self.comparison_tables:
                context["comparison_tables"] = self.comparison_tables[row_name]

            text = {
                "content": DynamicText(template_path, context),
                "file_name": row_name
            }
            print text["content"].as_html()
            self.texts.append(text)


    def save(self, file_format="html"):
        if not self.texts:
            self.render()

        for text in self.texts:
            file_path = "%s/%s.%s" % (self.output_folder, text["file_name"], file_format)
            if file_format == "md":
                content = text["content"].as_markdown()
            else:
                content = text["content"].as_html()

            with open(file_path, "w") as out_file:
                out_file.write(content.encode("utf-8"))
            

        
