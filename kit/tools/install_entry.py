"""Entry point for isolated Python CLI; import only sibling kit modules."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from install import main
if __name__=='__main__': sys.exit(main())
