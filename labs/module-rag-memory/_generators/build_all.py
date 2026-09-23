"""Rebuild every R-lab notebook and its solution:  python build_all.py"""
import lab_r1, lab_r2, lab_r3, lab_r4
from nbgen import write

write("lab-r1-hybrid-retrieval.ipynb", lab_r1.cells)
write("lab-r2-rerankers.ipynb", lab_r2.cells)
write("lab-r3-memory-policies.ipynb", lab_r3.cells)
write("lab-r4-ragas-evaluation.ipynb", lab_r4.cells)
