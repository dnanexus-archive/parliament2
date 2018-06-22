# Parliament2 Developer Readme

## Adding a structural variant caller

Parliament2 is currently optimized to run efficiently at scale with a number of structural variant callers. As a result, some SV callers have been excluded due to their longer runtimes. However, if you are not running Parliament2 at scale, you can add additional SV callers.

There are four main actions required in order to add an SV caller:

* Adding the SV caller and its dependencies to the Docker image
* Running the SV caller
* Converting the SV caller's outputs into VCF format
* Running SVTyper on the SV caller's outputs

### Adding the SV caller and its dependencies

If the SV caller can be installed using conda, pip, or another package installer, simply add a line reading `RUN <package_installer> install <CALLER>` to the Dockerfile. Otherwise, you will have to compile the SV caller code for an Ubuntu 14.04 machine and add it to the `resources.tar.gz` archive when building the Docker image. You can compile the SV caller code for an Ubuntu machine using a DNAnexus cloud workstation (available at https://platform.dnanexus.com/app/cloud_workstation with a DNAnexus account).

You will need to rebuild the Docker image, which can take up to 15 minutes and requires at least 5 GB of memory on your local machine, and create a DNAnexus asset from the Docker image, which can take up to an hour.

Steps involved:

* Download the Parliament2 files by running `git clone https://github.com/dnanexus/parliament2.git`. You will have to run `tar -czvf resources.tar.gz resources/` in the directory `parliament2` in order to build the Docker image. **Optional**: Add the requisite files for your SV caller into the `resources/` directory *or* modify the Dockerfile accordingly.

* Run `docker build . -t parliament2` from within the `parliament2` directory created by GitHub. There should now be a Docker image named `parliament2` on your computer. You can verify the successful installation using the command `docker images`, which will list every Docker image stored locally on your machine, or by running `docker run parliament2 -h`, which will print the help string (printed in full at the bottom of this README).

* Run `dx-docker create-asset parliament2`. This will take approximately 45 minutes and will generate a string that you can copy-paste into the `dxapp.json` file under the "Regional Options" section for your region.

* Run `dx build parliament2` to build the applet.

### Running the SV caller (`run_sv_callers.sh`)

In order to do this, you must first determine whether you can or can't parallelize the caller's execution by contig.

#### Parallelizing callers by contig

Splitting the BAM file by contig has already been taken care of; lines 103-167 comprise the block of code dedicated to running these callers.

You will need to modify the following sections:

* The `if` statement under the section "Process management for launching jobs"
* The "thread-checking" section

You will need to add the following lines:

* A check to see if the caller is being run (`if [[ "$run_CALLER" == "true" ]]`)
* Running the caller on a single contig with a timeout of 6h (`timeout 6h CALLER`)
* Defining a command to merge later (`CALLER_concat="$CALLER_concat CALLER.$count.vcf"`)

The best thing to do is to emulate how other callers are being run.

#### Running other callers

If the caller has a built-in method for parallelization, you can run it outside of the code block that splits the BAM file by contig.

You will need to add the following lines:

* A check to see if the caller is being run (`if [[ "$run_CALLER" == "true" ]]`)
* Running the caller

Examples of running other callers are demonstrated in the lines of code running BreakSeq and Manta.

### Converting the SV caller's outputs into VCF format (if applicable) (`convert_to_vcf.sh`)

In order to run SVTyper on the SV caller's outputs, they must first be converted to VCF format. This varies depending on whether the caller has been parallelized by contig or not.

#### Parallelized by contig

You will need to add the following lines:

* A check to see if the caller is being run (`if [[ "$run_CALLER" == "true" ]]`)
* A concatenation of the various files produced by the caller (`python /convertHeader.py "$prefix" "$CALLER_concat" | vcf-sort -c | uniq > CALLER.vcf`)
* Make a copy of the VCF file to add the prefix for upload (`cp CALLER.vcf "$prefix".CALLER.vcf`)
* Upload the VCF file

#### Callers run normally

If the caller's output files have not been split by contig, and the caller already produces outputs in VCF format, there is no need to do anything.

However, if the caller produces outputs in non-VCF format, you will have to write your own conversion script to convert the outputs to VCF format.

### Running SVTyper on the SV caller's outputs (`run_svtyper.sh`)

You will need to add the following lines:

* A check to see if the caller is being run (`if [[ "$run_CALLER" == "true" ]]`)
* A `mkdir` to capture SVTyper's outputs (`mkdir svtype_CALLER`)
* Running SVTyper itself (`timeout -k 500 60m ./parallelize_svtyper.sh /home/dnanexus/CALLER.vcf /home/dnanexus/svtype_CALLER /home/dnanexus/CALLER.svtyped.vcf input.bam`)

## Additional Information

If you require assistance with Parliament2, please contact <support@dnanexus.com>.