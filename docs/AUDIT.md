# Audit and hardening notes (October 2026)

This document records what was checked, what was found and what was changed when the project was prepared for public review. It exists so every change can be explained and defended. The work was prepared with AI assistance (Claude) and submitted as a pull request for the author's review.

Confidence labels: **CONFIRMED** (verified by running code or inspecting files), **LIKELY** (strong evidence, not proven), **HYPOTHESIS** (plausible, unverified).

## 1. Security and privacy

| Item | Finding | Status |
|---|---|---|
| `academia.db` | Valid SQLite file with the `alunos` schema and **0 rows**. `sqlite_sequence` is empty (no row was ever inserted), there are no free pages, and a byte scan found no leftover row data. | CONFIRMED: no personal data |
| `academia.db` in Git history | Added once in the first commit; the blob hash is identical in every commit that contains it, so history holds only the same empty file. | CONFIRMED: no history rewrite needed |
| `__pycache__/*.pyc` | Compiled bytecode committed by accident. Each file embeds the absolute path of the author's local folder on Windows (it reveals a local username and folder structure, nothing else). | CONFIRMED, low severity |
| Credentials / secrets | No passwords, tokens, keys or connection strings in any file or commit (4 commits checked). | CONFIRMED |
| Deleted `teste.py` | Matplotlib experiment with hard-coded sample numbers; no sensitive content. | CONFIRMED |
| `dados/alunos.txt` | Empty file, unused by the code. | CONFIRMED |
| SQL injection | All queries were already parameterized (`?` placeholders). A test now proves a malicious name is stored as plain text. | CONFIRMED |

**Actions:** the database, the `.pyc` files and the empty data file were removed from version control and are now ignored by `.gitignore` (which also ignores `*.db`, so real member data cannot be committed in the future). History was **not** rewritten: the only item still present in old commits is the local folder path inside the `.pyc` files, which is low risk. If the author wants it gone, see section 5.

## 2. Runtime bugs found and fixed

Each bug was reproduced against the original code before being fixed, and each fix has a regression test.

| # | Bug (original behavior) | Cause | Fix |
|---|---|---|---|
| 1 | Program crashed on startup: `ModuleNotFoundError: No module named 'lib.arquivo'` | `main.py` imported `lib.arquivo`, which was never committed. A name-by-name analysis showed `main.py` used **nothing** from it; every function it calls is defined in `lib.inter` or `lib.banco_de_dados`. | Removed the import. Reconstructing the module was unnecessary. |
| 2 | After editing a plan to weight training, the member disappeared from plan reports and averages | Typo: `editarPlanoBanco` stored `'musulacao'` | Correct spelling; `atualizarBanco()` also repairs existing rows that have the typo |
| 3 | Searching "Ana" did not find "ana" | Names are stored in lowercase, but search and age-edit did not lowercase the input | Names are normalized (trim + lowercase) inside the data layer for every operation |
| 4 | "Estatisticas por sexo" crashed on an empty database (`TypeError: cannot unpack non-iterable NoneType`) | `porSexoBanco()` returned `None` when there were no members | Returns `(0, 0)`; the chart is skipped when there is no data |
| 5 | Typing letters for plan or status crashed the program (`ValueError`) | `int(input())` without error handling in `leiaPlano`/`leiaStatus` | Both use the validated `leiaInt` |
| 6 | When input ended (closed stdin), the program printed about one million lines in 5 seconds and never stopped | The bare `except:` in `leiaInt` also caught `EOFError`, so it retried forever | Only `ValueError` is caught; `main.py` exits cleanly on `EOFError`/`KeyboardInterrupt` |
| 7 | Two reports never closed their database connection | `conexao.close()` was placed after `return` (unreachable) | Close before returning |
| 8 | Age report printed raw tuples: `Media geral: (30.0,)`, `Pilates: (None,)` | `fetchone()` result printed directly | Values formatted as `30.0 anos` or `sem dados` |
| 9 | `DeprecationWarning` on Python 3.12+ when registering | Relied on `sqlite3`'s default date adapter, deprecated in 3.12 | Date stored explicitly as ISO text (`date.isoformat()`) |
| 10 | Running from another folder created a new, empty `academia.db` in that folder | Relative database path | Path anchored to the project root; overridable with `GYM_DB_PATH` |
| 11 | No way to leave the program except `Ctrl+C` | No exit option | Added *Sair* (option 5) |

Small additions made while fixing the above: blank names are rejected, ages must be between 1 and 120, each chart opens in a fresh figure (they could overlap before), and search shows every member with the matching name instead of only the first.

**Origin of `lib.arquivo`:** HYPOTHESIS. The empty `dados/alunos.txt` file and the module name suggest an earlier version stored members in a text file before the switch to SQLite. No copy of the module exists in the repository history, so this could not be verified and nothing was reconstructed.

## 3. Dependencies

`requirements.txt` was saved in UTF-16 with CRLF line endings (LIKELY produced by `pip freeze > requirements.txt` in Windows PowerShell, whose `>` writes UTF-16) and pinned 11 transitive packages to versions from a Python 3.14 environment. It now contains only the direct dependency, `matplotlib>=3.8`, in UTF-8; pip resolves the rest for the user's Python version.

## 4. Test log

Environment: Linux, Python 3.13.17, Matplotlib 3.11.2 (pre-installed), `MPLBACKEND=Agg`. PyPI was not reachable from the sandbox used for this work, so `pip install -r requirements.txt` could not be executed there; the GitHub Actions workflow covers that step on a clean machine.

| Command | Result |
|---|---|
| `python -m unittest -v` | 50 tests, all passed (about 0.7 s) |
| Same data-layer and input tests against the **original** code | 28 + 10 run: 34 failed or errored; the EOF test hung until killed by a timeout. Many of these failures come from the original code not being testable (no configurable path, no return values); the regression tests named after bugs 2 to 6 fail for the bug itself. |
| `printf '' \| python main.py` | Exit code 0, one prompt, then "Encerrando o sistema." |
| Manual session with invalid name, age, sex, plan and status inputs | Each invalid value rejected with a message; record saved correctly |
| `python scripts/seed_demo_db.py` twice | First run created 20 members; second run refused to overwrite (exit code 1) |
| Every report against the demo database | All printed results; charts rendered without errors |

## 5. Optional: removing the old `.pyc` files from Git history

Not done, because it requires rewriting history and a force-push, which needs the author's decision. It is only worth doing if the local folder path should not remain visible in old commits.

```bash
# Work on a fresh mirror clone, never on your normal working copy
pip install git-filter-repo
git clone --mirror https://github.com/mateuscengeroff-prog/gym-management-system.git
cd gym-management-system.git
git filter-repo --path-glob '*.pyc' --invert-paths
# filter-repo removes the 'origin' remote as a safety measure; add it back
git remote add origin https://github.com/mateuscengeroff-prog/gym-management-system.git
git push --force --mirror origin   # rewrites history on GitHub
```

Afterwards every existing clone must be re-cloned, and open pull requests must be recreated.
