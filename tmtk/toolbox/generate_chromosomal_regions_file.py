import os


def generate_chromosomal_regions_file(platform_id=None, reference_build='hg19', **kwargs):
    """
    This creates a new chromosomal regions annotation file.

    :param platform_id: Give the new platform a name to fill first column
    :param reference_build: choose either hg18, hg19 or hg38
    :return: a pandas dataframe with the new platform
    """
    import rpy2.robjects as robjects
    import rpy2.robjects.pandas2ri as pandas2ri

    host_mapping = {'hg18': 'may2009.archive.ensembl.org',
                    'hg19': 'grch37.ensembl.org',
                    'hg38': 'www.ensembl.org'}
    mart_host = host_mapping[reference_build]

    only_y = kwargs.get('only_y', False)

    r_source = robjects.r['source']
    module_location = os.path.dirname(__file__)
    r_source(os.path.join(module_location, 'query_biomart.R'))
    r_query_mart = robjects.globalenv['query_biomart']
    r_check_install = robjects.globalenv['verify_biomart_install']

    if pandas2ri.Vector(r_check_install())[0] != 'INSTALLED':
        raise Exception('Cannot find biomaRt in R environment.'
                        'To install biomaRt, open R console and run:'
                        '\n\t>source("https://bioconductor.org/biocLite.R")'
                        '\n\t>biocLite("biomaRt")'
                        )

    new_platform = pandas2ri.ri2py_dataframe(r_query_mart(mart_host, platform_id, only_y))
    return new_platform
