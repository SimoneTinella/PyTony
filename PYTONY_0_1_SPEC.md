# Pytony 0.1 Specification

## Stato Del Documento

Questo documento definisce la specifica di riferimento di `Pytony 0.1`.

`Pytony 0.1` e una versione ibrida:

- ha una superficie sintattica propria;
- introduce costrutti esclusivi del linguaggio;
- si abbassa ancora verso Python per l'esecuzione finale.

Quando questa specifica e in conflitto con il comportamento accidentale del transpiler, la specifica descrive l'intento del linguaggio e il repo deve convergere verso di essa.

## Obiettivi Di Pytony 0.1

`Pytony 0.1` vuole essere:

- leggibile da chi conosce Python;
- riconoscibile come voce autonoma;
- eseguibile sopra il runtime Python senza VM propria;
- abbastanza stabile da supportare script, esempi e primi strumenti editor.

Non e obiettivo di `Pytony 0.1` essere ancora indipendente dal runtime Python.

## Modello Di Esecuzione

Un file `Pytony` viene:

1. letto come testo UTF-8;
2. riscritto dal compilatore nelle forme Python equivalenti;
3. validato e compilato dal runtime Python;
4. eseguito come modulo o script Python.

Le implementazioni di riferimento sono in:

- [pytony/compiler.py](/Users/simonetinella/Repositories/PyTony/pytony/compiler.py)
- [pytony/parser.py](/Users/simonetinella/Repositories/PyTony/pytony/parser.py)
- [pytony/lowering.py](/Users/simonetinella/Repositories/PyTony/pytony/lowering.py)
- [pytony/runtime.py](/Users/simonetinella/Repositories/PyTony/pytony/runtime.py)

## File E Modalita

### File `.pytony`

I file con estensione `.pytony` sono file `Pytony` veri e propri.

Per questi file:

- vale la modalita strict;
- il lessico canonico Pytony e obbligatorio quando esiste un alias ufficiale;
- l'import hook di `Pytony` puo caricare altri moduli `.pytony`.

### File `.py`

I file `.py` restano file Python normali.

Possono essere eseguiti tramite il runtime del progetto, ma:

- non sono in modalita strict;
- non hanno l'obbligo di usare il lessico Pytony;
- non fanno parte della sintassi definita da questa specifica.

## Regole Lessicali

### Encoding

Il testo sorgente e interpretato in UTF-8.

### Commenti

I commenti di riga iniziano con `#` e seguono le regole di Python.

### Stringhe

Le stringhe seguono la sintassi Python:

- apici singoli;
- doppi apici;
- triple-quoted;
- prefissi come `r`, `b`, `u`, `f` e combinazioni compatibili con Python.

Nelle stringhe normali il testo non viene riscritto.
Nelle f-string, le espressioni dentro `{...}` vengono transpiliate come codice Pytony.

### Indentazione

L'indentazione e significativa come in Python.
I blocchi sono introdotti da `:` e definiti dal livello di indentazione successivo.

### Nomi Riservati

In un file `.pytony`, i nomi elencati come keyword o built-in canonici di Pytony vanno considerati riservati al linguaggio.

In piu, i nomi interni che iniziano con `__pytony_ritornello_` sono riservati all'implementazione e non vanno usati intenzionalmente dal programma utente.

## Modalita Strict

La modalita strict si applica ai file `.pytony`.

Regola:

- se esiste un alias Pytony canonico per una keyword o un built-in Python supportato, la forma Python pura non e ammessa nel sorgente `.pytony`.

Esempi non ammessi in `.pytony`:

- `if`
- `True`
- `print`
- `len`
- `import`

Le stesse forme restano legali in file `.py`.

## Vocabolario Canonico

### Alias Delle Keyword

Ogni keyword Python ha un alias Pytony canonico.

| Pytony | Python |
| --- | --- |
| `mica_vero` | `False` |
| `solo_una_macchia` | `None` |
| `lapalissiano` | `True` |
| `e_poi` | `and` |
| `come_monet` | `as` |
| `te_l_ho_detto` | `assert` |
| `fuori_piove` | `async` |
| `aspetta_amore` | `await` |
| `fine_del_mondo` | `break` |
| `uomo_cannone` | `class` |
| `anche_stasera` | `continue` |
| `e_se_invece` | `elif` |
| `senno` | `else` |
| `ma_ehi` | `except` |
| `a_dopo_amore` | `finally` |
| `gira_il_circo` | `for` |
| `dal_divano` | `from` |
| `su_tutta_la_terra` | `global` |
| `e_se` | `if` |
| `you_might_also_like` | `import` |
| `nell_alta_marea` | `in` |
| `sei_proprio` | `is` |
| `colpo_di_scena` | `lambda` |
| `vicoli_stretti` | `nonlocal` |
| `mica` | `not` |
| `oppure` | `or` |
| `fai_finta` | `pass` |
| `mentre_riposi` | `while` |
| `strofa` | `def` |
| `mi_strappo` | `del` |
| `interludio` | `match` |
| `bridge` | `case` |
| `oh_oh` | `_` |
| `scoppia` | `raise` |
| `restero` | `return` |
| `sperimentiamo` | `try` |
| `con_la_coperta` | `with` |
| `sfiora_le_stelle` | `yield` |

### Alias Dei Built-in Supportati

`Pytony 0.1` definisce anche alias canonici per un primo gruppo di built-in Python.

| Pytony | Python |
| --- | --- |
| `spara_minchiate` | `print` |
| `pronto_amore` | `input` |
| `fai_la_pesata` | `len` |
| `viaggio_lontano` | `range` |
| `apri_il_portafoglio` | `open` |
| `schizzo_monet` | `str` |
| `duecento_euro` | `int` |
| `alta_marea` | `float` |
| `lapalissiano_o_mica` | `bool` |
| `popcorn` | `list` |
| `portafoglio` | `dict` |
| `mostri` | `set` |
| `coperta_calda` | `tuple` |
| `chi_siamo` | `type` |
| `lavarei_piatti` | `sum` |
| `meno_rossi` | `min` |
| `uomo_migliore` | `max` |
| `contale_tutte` | `enumerate` |
| `dammi_il_cuore` | `zip` |
| `di_lato` | `reversed` |
| `in_fusoliera` | `sorted` |
| `tutti_i_mostri` | `all` |
| `pure_uno` | `any` |
| `senza_arrossire` | `abs` |
| `a_crepapelle` | `round` |

## Struttura Dei Programmi

Un modulo `Pytony 0.1` e una sequenza ordinata di statement.

Gli statement supportati in forma nativa o stabilizzata sono:

- import semplice;
- `from ... import ...`;
- expression statement;
- assegnazione;
- assegnazione aumentata;
- `fai_finta`;
- `fine_del_mondo`;
- `anche_stasera`;
- `restero`;
- `scoppia`;
- `te_l_ho_detto`;
- `e_se` / `e_se_invece` / `senno`;
- `mentre_riposi`;
- `gira_il_circo`;
- `strofa`;
- `uomo_cannone`;
- `con_la_coperta`;
- `sperimentiamo` / `ma_ehi` / `senno` / `a_dopo_amore`;
- `interludio` / `bridge`.

## Espressioni

`Pytony 0.1` supporta le seguenti forme espressive come parte del linguaggio stabilizzato:

- nomi;
- stringhe;
- numeri;
- parentesi di raggruppamento;
- operatori unari `+`, `-`, `mica`;
- operatori binari `+`, `-`, `*`, `/`, `%`;
- operatori booleani `e_poi` e `oppure`;
- confronti;
- call;
- keyword arguments;
- attributi;
- indexing;
- slicing;
- list, tuple, dict e set literal;
- unpacking `*` e `**` nei casi supportati dall'implementazione;
- list comprehension;
- dict comprehension;
- set comprehension;
- generator expression;
- `colpo_di_scena`.

Le espressioni compatibili con Python ma non ancora rappresentate pienamente dall'AST nativo possono essere accettate in una modalita transizionale implementation-defined.

## Statement Principali

### Condizionali

La sintassi canonica e:

```py
e_se condizione:
    ...
e_se_invece altra_condizione:
    ...
senno:
    ...
```

Semantica:

- equivalente a `if` / `elif` / `else` di Python;
- la valutazione delle condizioni segue le regole di truthiness di Python.

### Loop `mentre_riposi`

La sintassi canonica e:

```py
mentre_riposi condizione:
    ...
senno:
    ...
```

La clausola `senno` e opzionale e segue la semantica di `while ... else` di Python.

### Loop `gira_il_circo`

La sintassi canonica e:

```py
gira_il_circo elemento nell_alta_marea iterabile:
    ...
senno:
    ...
```

La clausola `senno` e opzionale e segue la semantica di `for ... else` di Python.

### Funzioni

La sintassi canonica usa `strofa`:

```py
strofa saluta(nome):
    restero nome
```

Sono supportate:

- liste parametri semplici;
- annotazioni come sintassi Python quando accettate dal parser/lowering corrente;
- `restero` come forma canonica di `return`.

### Classi

La sintassi canonica usa `uomo_cannone`:

```py
uomo_cannone Cantante(Base):
    fai_finta
```

La semantica resta quella di `class` in Python.

### Gestione Errori

La sintassi canonica usa:

- `sperimentiamo`
- `ma_ehi`
- `senno`
- `a_dopo_amore`
- `scoppia`
- `te_l_ho_detto`

Esempio:

```py
sperimentiamo:
    scoppia RuntimeError("boom")
ma_ehi RuntimeError come_monet errore:
    spara_minchiate(errore)
a_dopo_amore:
    spara_minchiate("chiusura")
```

La semantica e quella di `try` / `except` / `else` / `finally` di Python.

### Context Manager

La sintassi canonica usa `con_la_coperta`:

```py
con_la_coperta apri_il_portafoglio("demo.txt") come_monet handle:
    spara_minchiate(handle.read())
```

La semantica e quella di `with`.

### Pattern Matching

La sintassi canonica usa:

- `interludio` per `match`
- `bridge` per `case`
- `oh_oh` per `_`

Esempio:

```py
interludio evento:
    bridge 1:
        spara_minchiate("uno")
    bridge oh_oh:
        spara_minchiate("altro")
```

`Pytony 0.1` considera stabile la struttura dello statement `match`.
La copertura dei pattern e parzialmente nativa e parzialmente transizionale.

## Pattern Supportati

I pattern seguenti sono parte del sottoinsieme stabile coperto dal parser nativo:

- wildcard `oh_oh`;
- capture pattern;
- literal pattern;
- value pattern;
- sequence pattern;
- star pattern;
- class pattern;
- `or` pattern;
- `as` pattern.

Pattern Python validi ma non ancora coperti pienamente dall'AST nativo possono essere accettati come comportamento transizionale.

## Costrutti Esclusivi Di Pytony

`Pytony 0.1` definisce tre costrutti esclusivi del linguaggio.

### `ritornello`

Sintassi:

```py
ritornello espressione:
    ...
```

Semantica:

- il blocco viene eseguito un numero di volte equivalente a `range(espressione)`;
- l'espressione viene valutata con la semantica di Python;
- l'implementazione usa un nome di loop interno riservato.

Equivalenza di riferimento:

```py
ritornello 3:
    spara_minchiate("ciao")
```

si abbassa a:

```py
for __pytony_ritornello_1 in range(3):
    print("ciao")
```

Il programma non deve affidarsi al nome interno generato.

### `duetto`

Sintassi:

```py
duetto target1, target2 con iterabile1, iterabile2:
    ...
```

Semantica:

- scorre piu iterabili in parallelo;
- si comporta come un `for` su `zip(...)`;
- il binding dei target segue la semantica Python del target di un `for`.

Equivalenza di riferimento:

```py
duetto nome, coro con nomi, cori:
    spara_minchiate(nome, coro)
```

si abbassa a:

```py
for nome, coro in zip(nomi, cori):
    print(nome, coro)
```

### `ancora_una_volta`

Sintassi:

```py
ancora_una_volta condizione:
    ...
```

Semantica:

- il blocco viene eseguito almeno una volta;
- dopo ogni iterazione viene valutata `condizione`;
- se la condizione e falsa, il loop termina.

Equivalenza di riferimento:

```py
contatore = 0
ancora_una_volta contatore < 3:
    spara_minchiate(contatore)
    contatore += 1
```

si abbassa a:

```py
contatore = 0
while True:
    print(contatore)
    contatore += 1
    if not (contatore < 3):
        break
```

## Import E Moduli

`Pytony 0.1` supporta:

- import di moduli Python normali;
- import di moduli `.pytony`;
- package `.pytony` con `__init__.pytony`.

La forma canonica usa `you_might_also_like` e `dal_divano`.

Esempi:

```py
you_might_also_like math
dal_divano musica you_might_also_like nota
```

Quando uno script viene eseguito tramite `pytony run`, l'import hook di riferimento permette di risolvere moduli `.pytony` lungo `sys.path`.

## Diagnostica

Gli errori di `Pytony 0.1` si dividono in due famiglie:

- errori lessicali o sintattici del linguaggio, esposti come `PytonySyntaxError` in strict mode;
- errori Python sollevati dal codice abbassato o dal runtime.

Il parser nativo di riferimento fornisce gia, per molti casi:

- messaggio in lessico Pytony;
- riga;
- colonna;
- puntatore visuale.

La forma esatta dei messaggi di errore non e ancora completamente standardizzata e resta implementation-defined, ma il contenuto semantico dell'errore deve restare comprensibile in termini Pytony.

## Compatibilita Con Python

La compatibilita di `Pytony 0.1` con Python va intesa cosi:

- il codice generato e Python valido;
- il runtime di esecuzione e Python;
- le strutture semantiche di base seguono Python;
- un file `.pytony` non coincide con un file Python arbitrario, perche in strict mode impone il vocabolario Pytony.

Quindi `Pytony 0.1` non e "Python con qualsiasi sintassi Python ammessa".
E "un linguaggio che si abbassa a Python".

## Zone Transizionali

Le aree seguenti non sono ancora completamente chiuse a livello di specifica:

- espressioni Python avanzate fuori dal sottoinsieme nativo;
- pattern avanzati di `match/case` non ancora rappresentati interamente nell'AST Pytony;
- alcune forme molto ricche di annotazioni, parametri o combinazioni espressive rare;
- dettagli di formattazione del codice generato.

In queste zone, `Pytony 0.1` accetta un comportamento implementation-defined purche:

- non contraddica il lessico canonico;
- non rompa la modalita strict;
- non tradisca la semantica Python di riferimento.

## Garanzie Di Stabilita

Per `Pytony 0.1` sono da considerare stabili:

- estensione `.pytony`;
- modalita strict per i file `.pytony`;
- vocabolario canonico elencato in questa specifica;
- costrutti esclusivi `ritornello`, `duetto`, `ancora_una_volta`;
- comandi principali `run`, `check`, `transpile`;
- import di moduli `.pytony` tramite runtime del progetto.

Sono ancora da considerare evolutivi:

- la completezza del parser nativo;
- la forma esatta della diagnostica;
- la copertura dell'editor support;
- eventuali futuri costrutti esclusivi a livello espressivo.

## Non Obiettivi Di 0.1

`Pytony 0.1` non promette ancora:

- una VM propria;
- indipendenza semantica totale da Python;
- un formatter ufficiale;
- un language server;
- una specifica completa di ogni costrutto Python esistente.

## Riferimenti

Documenti collegati:

- [README.md](/Users/simonetinella/Repositories/PyTony/README.md)
- [PYTONY_MANIFESTO.md](/Users/simonetinella/Repositories/PyTony/PYTONY_MANIFESTO.md)
- [PYTONY_LANGUAGE_ROADMAP.md](/Users/simonetinella/Repositories/PyTony/PYTONY_LANGUAGE_ROADMAP.md)
