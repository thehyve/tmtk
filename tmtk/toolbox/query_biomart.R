query_biomart <- function(mart_host, gpl_id, only_y=FALSE){

    # ### Using ensembl on GRCh37 -----------------------------------------------
    library(biomaRt)
    mart <- useMart(biomart = "ENSEMBL_MART_ENSEMBL",
                    dataset = "hsapiens_gene_ensembl",
                    host=mart_host)


    # Only use standard human chromosomes
    normal.chroms <- c(1:22, "X", "Y", "M")

    if (only_y) {
        normal.chroms = "Y"
    }

    # # Get the coordinates through biomart and merge with platform -------------
    entrez_list <- getBM(attributes = c("chromosome_name", "start_position", "end_position",
                                        "band", 'hgnc_symbol','entrezgene'),
                         filter = 'chromosome_name',
                         values = normal.chroms,
                         mart = mart)

    # Only keep entries with both HGNC symbol and Entrez gene ID
    entrez_list <- entrez_list[which(!is.na(entrez_list$entrezgene) & entrez_list$hgnc_symbol != ''),]

    # Deduplicate list from hgnc symbols
    entrez_list <- entrez_list[order(entrez_list$entrezgene),]
    entrez_list <- entrez_list[!duplicated(entrez_list$hgnc_symbol),]

    # Sorting based on chromomome and start position
    entrez_list <- entrez_list[order(entrez_list$chromosome_name, entrez_list$start_position),]

    ### Create platform file
    biomart_entrez_platform <- data.frame(  "GPL_ID" = gpl_id,
                                            "REGION_NAME" = entrez_list$hgnc_symbol,
                                            "CHR" = entrez_list$chromosome_name,
                                            "START_BP" = as.integer(entrez_list$start_position),
                                            "END_BP" = as.integer(entrez_list$end_position),
                                            "NUM_PROBES" = '',
                                            "CYTOBAND" = entrez_list$band,
                                            "GENE_SYMBOL" = entrez_list$hgnc_symbol,
                                            "GENE_ID" = entrez_list$entrezgene,
                                            "ORGANISM" = 'Homo sapiens'
                                    )
    return(biomart_entrez_platform)
}


verify_biomart_install <- function(){
    # Check whether biomart is installed and otherwise try to install.
    if (!is.element('biomaRt', installed.packages()[,1])) {
        print('biomaRt not found. Trying to download.')
        source("https://bioconductor.org/biocLite.R")
        biocLite("biomaRt")
        return("INSTALLED")
    } else {
        return("INSTALLED")
    }
}