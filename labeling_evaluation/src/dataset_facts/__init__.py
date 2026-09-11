"""Every measured fact about the labelled dataset, for the Preliminary Analysis.

The modules ``a1``–``a6`` follow Part A of the framework document
(``eVTOL_Methodology_Framework_v2_ANNOTATED_20260909.md``); ``index`` holds the
Preliminary Analysis index (v1.1) as data and says which tables and figures each
of its sections shows.

=============  ==========================================================
``loaders``    reads ``1639_LABELLED`` into a :class:`~loaders.Dataset`
``metrics``    the shared statistics (effective number, kappa, HHI, ...)
``a1``         A.1 information sources, inclusion gates, provenance, time coverage
``a2``         A.2 the first descriptive pass, checks D1-D13
``a3``         A.3 the derived per-aircraft layer (D2b)
``a4``         A.4 architecture from the text and its confirmation (appendix)
``a5``         A.5 aircraft names as they stand
``a6``         A.6 the identity variables (appendix)
``roster``     the aircraft that enter the analysis, with every sensitivity flag
``rules``      D12 — the 02a consistency-rule counts
``index``      the Preliminary Analysis index as data (Source / Tables / Gives)
``figures``    every figure, matplotlib, monochrome
``report``     the draft PRELIMINARY_ANALYSIS.md assembled from index + tables
``published``  every number the framework document prints, checked live
``export``     all tables -> CSV + markdown
=============  ==========================================================

Every public function returns a :class:`pandas.DataFrame`, a dict or a Figure, so
``labeling_evaluation/notebooks/30_preliminary_analysis.ipynb`` only imports,
calls and displays. Configuration: ``labeling_evaluation/config.yaml``. Nothing
here writes to the dataset.
"""

from .loaders import Dataset, load_dataset  # noqa: F401

__all__ = ["Dataset", "load_dataset"]
