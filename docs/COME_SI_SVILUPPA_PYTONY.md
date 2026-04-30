# Come Si Sviluppa Pytony

Questa guida spiega come è costruito `Pytony` e come si contribuisce alla sua evoluzione.

## Visione D'Insieme

`Pytony` oggi è un linguaggio che:

1. legge codice `.pytony`;
2. applica riscritture lessicali e costrutti esclusivi;
3. costruisce o usa un AST di lavoro;
4. abbassa il risultato a Python;
5. esegue il Python generato.

## Componenti Principali

### 1. Compiler

File:
- [pytony/compiler.py](/Users/simonetinella/Repositories/PyTony/pytony/compiler.py)

Responsabilità:
- alias keyword e built-in;
- strict mode per i file `.pytony`;
- transpile delle f-string;
- riscrittura dei costrutti esclusivi.

### 2. Parser

File:
- [pytony/parser.py](/Users/simonetinella/Repositories/PyTony/pytony/parser.py)

Responsabilità:
- parsing nativo di statement ed espressioni;
- diagnostica sintattica;
- gestione di parte dei pattern `match/case`.

### 3. AST

File:
- [pytony/ast_nodes.py](/Users/simonetinella/Repositories/PyTony/pytony/ast_nodes.py)

Responsabilità:
- rappresentare la struttura del programma in forma manipolabile.

### 4. Lowering

File:
- [pytony/lowering.py](/Users/simonetinella/Repositories/PyTony/pytony/lowering.py)

Responsabilità:
- trasformare l'AST di Pytony in Python leggibile e valido.

### 5. Runtime

File:
- [pytony/runtime.py](/Users/simonetinella/Repositories/PyTony/pytony/runtime.py)

Responsabilità:
- esecuzione;
- transpile da file;
- validazione;
- formattazione su file.

### 6. Formatter

File:
- [pytony/formatter.py](/Users/simonetinella/Repositories/PyTony/pytony/formatter.py)

Responsabilità:
- imporre uno stile canonico di scrittura.

### 7. CLI

File:
- [pytony/cli.py](/Users/simonetinella/Repositories/PyTony/pytony/cli.py)

Responsabilità:
- esporre i comandi:
  - `run`
  - `transpile`
  - `check`
  - `fmt`

## Flusso Di Lavoro Tipico

### Eseguire un file

```bash
pytony run examples/hello.pytony
```

### Vedere il Python generato

```bash
pytony transpile examples/exclusive.pytony
```

### Validare il sorgente

```bash
pytony check examples/mood.pytony
```

### Formattare il sorgente

```bash
pytony fmt examples/exclusive.pytony
```

## Come Aggiungere Un Alias

Per aggiungere un alias:

1. aggiorna [pytony/compiler.py](/Users/simonetinella/Repositories/PyTony/pytony/compiler.py);
2. evita duplicati;
3. verifica che il nome sia coerente con la voce del linguaggio;
4. aggiungi o aggiorna i test;
5. aggiorna la documentazione.

## Come Aggiungere Un Nuovo Costrutto

Per aggiungere un costrutto esclusivo:

1. definisci la semantica nel documento di specifica;
2. decidi se è una semplice riscrittura o se richiede parsing nativo;
3. implementa la trasformazione;
4. aggiungi esempi;
5. aggiungi test di transpile e di esecuzione;
6. aggiorna il percorso didattico.

## Come Aggiungere Un Concetto Didattico

Per trasformare `Pytony` in un linguaggio sempre più didattico:

1. individua il concetto da insegnare;
2. scrivi un esempio minimo;
3. scrivi una spiegazione in linguaggio semplice;
4. collega sempre il costrutto Pytony al concetto generale di programmazione;
5. quando utile, mostra l'equivalente Python.

## Come Verificare Le Modifiche

Comandi utili:

```bash
python3 -m unittest discover -s tests -v
pytony check examples/exclusive.pytony
pytony fmt --check examples/exclusive.pytony
```

## Obiettivo Di Questa Guida

Questa guida non serve solo a dire "dove sta il codice".
Serve a rendere il progetto leggibile anche come laboratorio didattico:

- per chi studia i linguaggi;
- per chi vuole contribuire;
- per chi vuole insegnare programmazione con `Pytony`.
