# Pytony Language Support For VS Code

Questa cartella contiene il primo supporto editor ufficiale per `Pytony` su VS Code.

Include:

- riconoscimento automatico dei file `.pytony`;
- syntax highlighting per keyword, built-in e costrutti esclusivi;
- commenti, stringhe, numeri e definizioni di funzioni/classi;
- regole base di indentazione per blocchi Pytony.

## Installazione Locale

Il modo piu semplice e collegare questa cartella tra le estensioni locali di VS Code:

```bash
mkdir -p ~/.vscode/extensions
ln -s /Users/simonetinella/Repositories/PyTony/editors/vscode ~/.vscode/extensions/pytony-language-0.1.0
```

Poi riavvia VS Code oppure esegui `Developer: Reload Window`.

## File Principali

- [package.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/package.json)
- [language-configuration.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/language-configuration.json)
- [syntaxes/pytony.tmLanguage.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/syntaxes/pytony.tmLanguage.json)

## Stato Attuale

Questa prima versione punta a dare subito un buon highlighting.
Il prossimo livello naturale e aggiungere:

- snippets Pytony;
- tema o token color customizzati;
- language server o almeno diagnostics live;
- formatter dedicato.
