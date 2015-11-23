# -*- coding: utf-8 -*-

from computed_columns import *
from agate import Formula, Text, Number, Boolean

key = "municipality"
SETTINGS = {
    "data_source": {
        # Source of data
        "csv": "data.csv",
        "delimiter": ",",
        # A column name in the csv file used to identify rows (also name of output file). 
        "key": key,
        # Optional: A list of category columns that will be available for comparison in text template
        "compare_categories": ["county",],
        # Optional: Compute new columns
        "computed_columns": {
            u"consecutive_development": (Formula(Text(), consecutive_development)),
            u"is_growing": (Formula(Boolean(), is_growing)),
            u"change2014_perc_rank_in_county": GroupPercentileRank(group_by="county", rank_by="change2014", key=key, reverse=True)
        }
    },
    # Name of template file
    "template": "template.html"
}

