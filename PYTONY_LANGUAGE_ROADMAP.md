# Pytony Language Roadmap

Questo file segna il passaggio da "dialetto transpiled di Python" a linguaggio vero.

## Fase 0

Stato di partenza:

- alias lessicali Pytony -> Python;
- transpiler basato su token;
- esecuzione appoggiata direttamente al runtime Python;
- regola strict nei file `.pytony`.

## Fase 1

Primo milestone implementato in questa repo:

- AST interno di Pytony in [pytony/ast_nodes.py](/Users/simonetinella/Repositories/PyTony/pytony/ast_nodes.py)
- parser di milestone in [pytony/parser.py](/Users/simonetinella/Repositories/PyTony/pytony/parser.py)
- lowering verso Python in [pytony/lowering.py](/Users/simonetinella/Repositories/PyTony/pytony/lowering.py)
- parser nativo di espressioni per un primo sottoinsieme del linguaggio
- import di moduli `.pytony` tramite runtime dedicato
- comando `check` per validazione senza esecuzione

Il sottoinsieme coperto oggi comprende:

- espressioni-statement;
- assegnazioni;
- assegnazioni aumentate;
- `pass`, `break`, `continue`;
- `if` / `elif` / `else`;
- `while`;
- `for`;
- `def`;
- `class`;
- `with`;
- `match` / `case`;
- `return`.
- `raise`;
- `assert`.
- `try` / `except` / `else` / `finally`.

Le espressioni native coperte oggi comprendono:

- nomi;
- literal stringa e numero;
- call annidate;
- attributi;
- indexing;
- slicing;
- list literal;
- tuple, dict e set literal di base;
- list comprehension con clausole `for` e `if`;
- dict comprehension;
- set comprehension;
- generator expression;
- lambda semplice;
- keyword arguments nelle call;
- unpacking `*` e `**` nei casi base;
- operatori unari `+`, `-`, `not`;
- operatori binari `+`, `-`, `*`, `/`, `%`;
- confronti;
- operatori booleani `and` e `or`;
- parentesi di raggruppamento.

Le espressioni piu avanzate non ancora supportate dal parser nativo ricadono per ora in una modalita raw transizionale.

Nei file `.pytony` strict, gli errori di parsing nativo iniziano anche a tornare come errori Pytony invece di degradare sempre in silenzio.
In piu, i parser statement-level nativi mostrano ora riga, colonna e puntatore visuale nei casi di errore piu comuni.
Anche i pattern piu comuni di `match` / `case` iniziano ora ad avere un AST nativo invece di restare solo testo.

## Fase 2

Passi successivi consigliati:

- estendere il parser nativo delle espressioni Pytony a slicing avanzato, attributi/call complessi, unpacking piu ricco e lambda piu ricche;
- ampliare gli errori di parsing con terminologia Pytony a tutto il compilatore, non solo ai casi strict gia coperti;
- AST separato da Python anche per operatori, call e literal;
- package system e import di moduli `.pytony` piu ricco, inclusi casi di package complessi e cache dedicata.
- togliere progressivamente i fallback raw sulle espressioni avanzate.

## Fase 3

Quando questi blocchi saranno completi, Pytony iniziera ad avere:

- grammatica propria;
- semantica interna piu esplicita;
- spazio per introdurre costrutti esclusivi del linguaggio.
