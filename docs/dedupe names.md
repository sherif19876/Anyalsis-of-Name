# Excel-Duplicate-Remover
This script reads an Excel file, checks for duplicate values in a specified column (default Name), reports how many times each duplicate appears, removes all but the first occurrence of each duplicate, and saves the deduplicated data to a new Excel file.
Key features:

Configurable column name (not hardcoded to Name – easily changeable via function parameter).

Clear console output showing each duplicate value and its frequency.

Preserves the first occurrence of each duplicate, dropping subsequent ones.

Saves cleaned data to a separate file without overwriting the original.

Use case:
Ideal for cleaning contact lists, membership rosters, survey responses, or any Excel-based dataset where rows should be unique based on a key column (e.g., name, email ID, product code).
