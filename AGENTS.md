# Storefront repository guidance

- The public storefront source of truth is `index.html` on `main` in the `goel-store/goel-store.github.io` repository. Check the remote and current branch before editing; other local checkouts may be stale or contain uncommitted work.
- Never replace the whole storefront with a snapshot from an older commit or checkout. Preserve current catalog, checkout, stock, navigation, and new-arrival changes; make focused edits and review `git status` before staging.
- Catalog and brand lists use `sortItemsByAvailability` in `index.html`. Keep in-stock items ahead of unavailable items, then prioritize `newArrival`, then newer catalog entries. Apply the same ordering in both catalog views.
- Before removing or renaming product images, verify that no active catalog item references them.
- Before publishing, run `git diff --check`, validate the inline JavaScript syntax, and confirm the GitHub Pages workflow completes successfully.
