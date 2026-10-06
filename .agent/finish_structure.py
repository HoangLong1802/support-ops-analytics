"""Finish the SQL relocation, accepting the original UTF-8 BOM."""
from pathlib import Path

path = Path(__file__).with_name('refine_structure.py')
source = path.read_text(encoding='utf-8')
source = source[source.index('schema = ROOT'):]
source = source.replace("read_text(encoding='utf-8')", "read_text(encoding='utf-8-sig')")
exec('from pathlib import Path\nimport json\nimport re\nROOT = Path(__file__).resolve().parents[1]\n' + source)
