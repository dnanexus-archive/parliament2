from setuptools import setup, find_packages

version = "Unknown"
for line in open("breakseq2/_version.py"):
    if line.startswith("__version__"):
        version = line.strip().split("=")[1].strip()

print version
setup(
      name='BreakSeq2',
      version=version,
      description='BreakSeq2: Ultrafast and accurate nucleotide-resolution analysis of structural variants',
      author='Bina Technologies',
      author_email='rd@bina.com',
      url='https://github.com/bioinform/breakseq2',
      packages = find_packages(),
      install_requires = ["cython", "pysam==0.7.7", "biopython==1.65"],
      scripts=['scripts/run_breakseq2.py', 'scripts/breakseq2_gen_bplib.py'],
      dependency_links = ["https://pypi.python.org/packages/source/p/pysam/pysam-0.7.7.tar.gz"]
      )
