# encoding: utf-8

""" Define computed columns here
"""

value_columns = ["y2000","y2001","y2002","y2003","y2004","y2005","y2006","y2007","y2008","y2009","y2010","y2011","y2012","y2013","y2014",]
change_columns = ["change2001","change2002","change2003","change2004","change2005","change2006","change2007","change2008","change2009","change2010","change2011","change2012","change2013","change2014",]

def consecutive_development(row):
    growing_last_year = row["change2014"] > 0
    n = 0
    for col in reversed(change_columns):
        growing_this_year = row[col] > 0
        if growing_last_year == growing_this_year:
            n = n + 1
        else:
            break
    return n


def is_growing(row):
    return row["change2014"] > 0


from decimal import Decimal
from agate import Number, Text, Computation, Rank, PercentileRank, Table

class GroupComparison(Computation):
    """ A base class for group comparisons.
        A key (column that holds row names) is required
        Init by passing either column name to group_by or a column consisting
        of comma separated keys to compare with. 

        Inheriting classes should define a _get_computation function
        that returns a computation that is applied to the grouped tables.
    """
    def __init__(self, key, group_by=None, comparison_column=None):
        """ key: column name containing unique key (String)
            group_by: name of column to group by (String)
            comparison_column: name of column with list if keys of rows to compare with (String)
        """
        self.key = key
        self.group_by = group_by
        self.comparison_column = comparison_column
        self._computed_col = "computed_"

    def _get_computation(self):
        """ Should return a computation named "computed_value"
            Like so: ( "computed_value", Rank(self.rank_by) )
        """
        raise NotImplementedError("No computation defined")

    def prepare(self, table):
        """ Prepare a table with comparison items for each row in table
        """
        super(GroupComparison, self).prepare(table)
        self.comparison_tables = {}

        if self.group_by:
            """ Case: Group by category column
            """
            self.groups = {}
            for group_table in table.group_by(self.group_by):
                # Add row name to the grouped tables
                group_table = Table(group_table.rows,
                    column_types=group_table.column_types,
                    column_names=group_table.column_names,
                    row_names=self.key)
                group_name = group_table.rows[0][self.group_by]

                # Apply computation
                group_table = group_table.compute([self._get_computation()])

                self.groups[group_name] = group_table

            for row in table.rows:
                row_key = row[self.key]
                group_name = row[self.group_by]
                self.comparison_tables[row_key] = self.groups[group_name]


        elif self.comparison_column:
            """ Case: Get comparison items from column
            """
            for row in table.rows:
                try:
                    comparison_keys = row[self.comparison_column].split(",")
                except AttributeError:
                    comparison_keys = []

                # Add self to comparison table. Needed to be able to rank
                comparison_keys += [row[self.key]]
                comparison_table = Table(
                    [table.rows[x] for x in comparison_keys],
                    column_types=table.column_types,
                    column_names=table.column_names,
                    row_names=self.key
                )
                # Apply computation
                comparison_table = comparison_table.compute([self._get_computation()])
                self.comparison_tables[row[self.key]] = comparison_table
        
    def run(self, row):
        row_key = row[self.key]
        comparison_table = self.comparison_tables[row_key]
        value = comparison_table.rows[row_key]["computed_value"]
        return Decimal(value)


class GroupRank(GroupComparison):
    def __init__(self, rank_by, key, reverse=False, group_by=None, comparison_column="comparison"):
        super(GroupRank, self).__init__(key, group_by=group_by, comparison_column=comparison_column)
        self.rank_by = rank_by
        self.reverse = reverse

    def get_computed_data_type(self, table):
        return Number()

    def _get_computation(self):
        return ( "computed_value", Rank(self.rank_by, reverse=self.reverse) )

class GroupPercentileRank(GroupRank):
    def _get_computation(self):
        return ( "computed_value", PercentileRank(self.rank_by, reverse=self.reverse) )

