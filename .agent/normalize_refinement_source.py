"""Keep changed Python files in the original predominantly LF source style."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ('src/build_portfolio.py', 'src/clean_data.py', 'src/run_pipeline.py', 'tests/test_pipeline.py', 'tools/synthetic_data_generator.py', 'tools/validate_generation.py'):
    path = ROOT / relative
    path.write_bytes(path.read_text(encoding='utf-8-sig').encode('utf-8'))
print('Changed Python source uses consistent LF newlines; logic unchanged.')
