import argparse
import vcf
import pandas as pd
import os
import itertools
import copy
FILTERED_CHROMS = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21",
    "22", "X", "Y"
]
FILTERED_CHROMS += ["chr" + num for num in FILTERED_CHROMS]

# imports for vcf.Reader
cparse = None
from vcf.model import _Call, _Record, make_calldata_tuple
from vcf.model import _Substitution, _Breakend, _SingleBreakend, _SV


class VCFReader(vcf.Reader):
    '''Inherit from the pyVCF reader class so we can add some bug fixes'''
    def _parse_samples(self, samples, samp_fmt, site):
        '''Parse a sample entry according to the format specified in the FORMAT
        column.
        NOTE: this method has a cython equivalent and care must be taken
        to keep the two methods equivalent
        '''

        # check whether we already know how to parse this format
        if samp_fmt not in self._format_cache:
            self._format_cache[samp_fmt] = self._parse_sample_format(samp_fmt)
        samp_fmt = self._format_cache[samp_fmt]

        if cparse:
            return cparse.parse_samples(
                self.samples, samples, samp_fmt, samp_fmt._types, samp_fmt._nums, site)

        samp_data = []
        _map = self._map

        nfields = len(samp_fmt._fields)

        for name, sample in itertools.izip(self.samples, samples):

            # parse the data for this sample
            sampdat = [None] * nfields

            for i, vals in enumerate(sample.split(':')):
                # make sure there's no extra fields
                if i > nfields - 1:
                    break
                # short circuit the most common
                if samp_fmt._fields[i] == 'GT':
                    sampdat[i] = vals
                    continue
                # genotype filters are a special case
                elif samp_fmt._fields[i] == 'FT':
                    sampdat[i] = self._parse_filter(vals)
                    continue
                elif not vals or vals == ".":
                    sampdat[i] = None
                    continue

                entry_num = samp_fmt._nums[i]
                entry_type = samp_fmt._types[i]

                # we don't need to split single entries
                if entry_num == 1:
                    if entry_type == 'Integer':
                        try:
                            sampdat[i] = int(vals)
                        except ValueError:
                            sampdat[i] = float(vals)
                    elif entry_type == 'Float' or entry_type == 'Numeric':
                        sampdat[i] = float(vals)
                    else:
                        sampdat[i] = vals
                    continue

                vals = vals.split(',')
                if entry_type == 'Integer':
                    try:
                        sampdat[i] = _map(int, vals)
                    except ValueError:
                        sampdat[i] = _map(float, vals)
                elif entry_type == 'Float' or entry_type == 'Numeric':
                    sampdat[i] = _map(float, vals)
                else:
                    sampdat[i] = vals

            # create a call object
            call = _Call(site, name, samp_fmt(*sampdat))
            samp_data.append(call)

        return samp_data


def read_vcf(vcf_f):
    vcf_reader = VCFReader(open(vcf_f, 'r'))
    return vcf_reader

def _extract_stats(record, label=None, svcaller_names=[]):
    # note: CI is confidence interval. For confidence intervals with multiple values, we're going to take the average.
    if isinstance(record.INFO['CIPOS'], list):
        record.INFO['CIPOS'] = [int(s) for s in record.INFO['CIPOS']]
        record.INFO['CIPOS'] = sum(record.INFO['CIPOS'])/len(record.INFO['CIPOS'])

    if isinstance(record.INFO['CIEND'], list):
        record.INFO['CIEND'] = [int(s) for s in record.INFO['CIEND']]
        record.INFO['CIEND'] = sum(record.INFO['CIEND'])/len(record.INFO['CIEND'])

    stats = {
        'chrom': record.CHROM,
        'start_pos': record.POS,
        'start_pos_ci': int(record.INFO['CIPOS']),
        'end_pos': record.INFO['END'],
        'end_pos_ci': int(record.INFO['CIEND']),
        'sv_type': record.INFO['SVTYPE'],
        'sv_length': abs(int(record.INFO['SVLEN'])),
        'same_strand': 1 if record.INFO['STRANDS'][0] == record.INFO['STRANDS'][1] else 0,
        'num_supps': sum(int(r) for r in record.INFO['SUPP_VEC']),
        'label': record.FILTER[0] if len(record.FILTER) > 0 else "PASS"
        }

    # Convert support vector into 0-1 encoding in matrix
    num_callers = len(record.INFO['SUPP_VEC'])
    for indx in range(num_callers):
        if indx > len(svcaller_names) - 1:
            key='sv_caller_{0}'.format(indx)
        else:
            key = 'supp_{0}'.format(svcaller_names[indx])
        value = record.INFO['SUPP_VEC'][indx]
        stats[key]=value

    if label is not None:
        stats['label'] = int(label)

    return stats

def main(vcf, output=None, ref=None, no_alts=False, caller_names=[]):
    matrix_rows = []

    vcf_reader = read_vcf(vcf)
    if ref is not None:
        ref_reader = read_vcf(ref)
    else:
        ref_reader = None

    for variant in vcf_reader:
        if no_alts is True and variant.CHROM not in FILTERED_CHROMS:
            continue
        elif 'SUPP_VEC' not in variant.INFO:
            continue

        # fetch the corresponding ref_variant
        if ref_reader is None:
            stats = _extract_stats(variant, svcaller_names=caller_names)
        else:
            ref_variant = ref_reader.fetch(variant.CHROM, variant.POS, variant.POS + variant.INFO['END'])
            try:
                label = ref_variant.INFO['SUPP_VEC'][1]
            except AttributeError:
                try:
                    ref_record = ref_variant.next()
                    label = ref_record.INFO['SUPP_VEC'][1]
                except (StopIteration, KeyError):
                    label = 0

            stats = _extract_stats(variant, label, svcaller_names=caller_names)
        matrix_rows.append(stats)

        df = pd.DataFrame(matrix_rows)

    if output is not None:
        output_f = output
    else:
        prefix = os.path.basename(vcf).replace('.vcf', '')
        output_f = prefix + '.csv'

    columns = sorted(stats.keys())
    # check if file exists
    if os.path.exists(output_f):
        df.to_csv(output_f, index=False, header=False, mode='a',
              columns = columns)
    else:
        df.to_csv(output_f, index=False, header=True, mode='w',
              columns = columns)

def _parse_args():
    '''Parse the input arguments.'''
    ap = argparse.ArgumentParser(description='VCF dataloader')

    ap.add_argument('--vcf', '-v',
                    help='VCF input',
                    required=True)

    ap.add_argument('--ref', '-m',
                    help='Training set compared with truth set',

                    required=False)    
    ap.add_argument('--output', '-o',
                    help='Output Filename',
                    required=False)    
    ap.add_argument('--no-alts', '-a',
                    help='Filter any variants in alt regions',
                    required=False,
                    action="store_true")
    ap.add_argument('--caller-names', '-s',
                    help='Supply SV caller names for header',
                    required=False,
                    action='append')
    return ap.parse_args()

if __name__ == '__main__':
    args = _parse_args()
    main(args.vcf, args.output, args.ref, args.no_alts, args.caller_names)
