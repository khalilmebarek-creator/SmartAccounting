"""Fix remaining try/except pass blocks by adding logging."""
import re, pathlib

REPLACEMENTS = [
    # (file, old_exact, new_exact)
    ("modules/bank_sync.py",
     "                    except Exception:\n                        pass\n\n            return {",
     "                    except Exception:\n                        get_logger('bank_sync').debug('Failed to parse transaction', exc_info=True)\n\n            return {"),

    ("modules/excel_export.py",
     "            except Exception:\n                pass\n\n    def _add_ratios_sheet",
     "            except Exception:\n                get_logger('excel_export').debug('Failed to add chart', exc_info=True)\n\n    def _add_ratios_sheet"),

    ("modules/print_manager.py",
     "        except Exception:\n            pass\n\n",
     "        except Exception:\n            get_logger('print_manager').debug('Failed to cleanup temp dir', exc_info=True)\n\n"),

    ("modules/update_checker.py",
     "            try:\n                f.close()\n            except Exception:\n                pass",
     "            try:\n                f.close()\n            except Exception:\n                pass  # noqa: B110 — best-effort close in finally"),

    ("modules/update_checker.py",
     "                try:\n                    os.remove(path)\n                except Exception:\n                    pass",
     "                try:\n                    os.remove(path)\n                except Exception:\n                    pass  # noqa: B110 — best-effort cleanup"),
]

base = pathlib.Path(r"C:\Users\khalile\Desktop\Accounting_Platform")

for fname, old, new in REPLACEMENTS:
    fp = base / fname
    content = fp.read_text(encoding="utf-8")
    if old in content:
        content = content.replace(old, new, 1)
        fp.write_text(content, encoding="utf-8")
        print(f"FIXED: {fname}")
    else:
        print(f"SKIP:  {fname} (pattern not found)")
