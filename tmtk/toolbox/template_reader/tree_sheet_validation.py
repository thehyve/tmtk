import pandas as pd

EXPECTED_HEADER = ['tranSMART data type', 'Sheet name/File name', 'Column Name']
OPTIONAL_HEADER = ['Data type', 'Ontology Code']

DATA_TYPE_VALUES = ['DATE', 'TEXT', 'NUMERICAL', 'CATEGORICAL']


def validate_tree_sheet(tree_sheet):
    # Validate column headers
    # - Datatype
    # - Sheet name/File name
    # - Column name
    # - Level X etc.
        # - Check for metadata fields
    # - Check for optional columns: Ontology code, Data type
    tree_sheet.columns = list_to_upper_underscore(tree_sheet.columns)
    validate_column_header(tree_sheet.columns)

    # If Sheet name is empty but Column name is not print, raise error and return line numbers
    source_columns  = tree_sheet.loc[:,['SHEET_NAME/FILE_NAME','COLUMN_NAME']].apply(check_source_columns(), axis=1)
    if source_columns.any():
        line_numbers = (source_columns[source_columns == True].index+1).tolist()
        msg = 'Error! Missing source sheet or file name for filled in column on lines {}'.format(line_numbers)
        print(msg)
        raise KeyError(msg)




    # Check if any fields in the "data" have a # (as it is the comment char print error (ADVANCED CHECK)


    # Return True if succesfull. If Errors encountered for now Raise KeyError
    return True


def validate_column_header(columns):
    l = []
    for item in EXPECTED_HEADER:
        item_ = item.upper().replace(' ','_')
        if item_ in columns:
            columns.pop(columns.index(item_))
        else:
            l.append(item_)

    # Process LEVEL and OPTIONAL_HEADERS

    if l != []:
        # TODO: Logger --> Also remove Raise, want human readable errors
        raise KeyError('Error! Missing the expected columns from the Tree sheet: {}'.format(l))



def list_to_upper_underscore(input_) -> list:
    return [item.upper().replace(' ','_') for item in input_]


def check_source_columns(item) -> bool:
        if pd.isnull(item[0]) and pd.notnull(item[1]):
            return True
        else:
            return False

