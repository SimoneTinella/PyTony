# Pytony Language Support For VS Code

Questa cartella contiene il primo supporto editor ufficiale per `Pytony` su VS Code.

Include:

- riconoscimento automatico dei file `.pytony`;
- syntax highlighting per keyword, built-in e costrutti esclusivi;
- snippet pronti per `e_se`, `strofa`, `ritornello`, `duetto`, `ancora_una_volta`, `interludio` e `sperimentiamo`;
- diagnostica live direttamente nell'editor tramite `pytony lint`;
- commenti, stringhe, numeri e definizioni di funzioni/classi;
- regole base di indentazione per blocchi Pytony.

## Installazione Locale

Il modo piu semplice e collegare questa cartella tra le estensioni locali di VS Code:

```bash
mkdir -p ~/.vscode/extensions
ln -s /Users/simonetinella/Repositories/PyTony/editors/vscode ~/.vscode/extensions/pytony-language-0.1.0
```

Poi riavvia VS Code oppure esegui `Developer: Reload Window`.

## Diagnostica Live

L'estensione esegue `pytony lint` sui file `.pytony` aperti e mostra warning o errori dentro l'editor.

Se nella tua shell `pytony` non e disponibile, puoi configurare VS Code cosi:

```json
{
  "pytony.lint.command": "python3",
  "pytony.lint.args": ["-m", "pytony"],
  "pytony.lint.run": "onSave"
}
```

Comando disponibile nella Command Palette:

- `Pytony: Esegui Lint Sul File Corrente`

## File Principali

- [package.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/package.json)
- [language-configuration.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/language-configuration.json)
- [syntaxes/pytony.tmLanguage.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/syntaxes/pytony.tmLanguage.json)
- [snippets/pytony.code-snippets](/Users/simonetinella/Repositories/PyTony/editors/vscode/snippets/pytony.code-snippets)

## Stato Attuale

Questa prima versione punta a dare subito un buon highlighting e una prima esperienza di scrittura guidata.
Il prossimo livello naturale e aggiungere:

- tema o token color customizzati;
- integrazione piu stretta con `pytony fmt` e `pytony lint`.
