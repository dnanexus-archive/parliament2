<!-- dx-header -->

## What does this app do?

This app extracts VCF features and one-hot encoding of various variant caller
outputs and produces a model to assign confidence scores to various identified
structural variants.

## What are typical use cases for this app?

Given identified variants from an ensemble variant calling approach and a 
validation or truth set, this app will create a model for assigning confidence 
scores to structural variants.

## What data are required for this app to run?

This app requires VCF files from various variant callers and a validation truth set.

## What does this app output?

This app will output a pickle (`*.pkl`) containing model parameters which can 
be used to predict confidence scores for a set of structural variants. In 
addition, this app will output logs containing accuracy scores for the 
training and validation sets.

## Recommended Validation Datasets

1000 Genomes Validation Set:
ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/hgsv_sv_discovery/working/integration/20170322_Validation_Set_Illumina_PacBio_indel/README.20170322.validation_set_for_illumina_pacbio_indels

Truth Set:
HG00514 
Parliament2 outputs:
https://platform.dnanexus.com/projects/FQ0xkxQ0xVZ0fjYV18xJVK28/monitor/job/FQ1PKx00xVZ0fjYV18xJVg9K
