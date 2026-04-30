![Pytony](<pytony.png>)

# Pytony

Pytony è un linguaggio di programmazione costruito sopra Python, ma parlato come se Python fosse finito dentro una canzone di Tony Pitony.

Non cerca più di essere solo Python con gli alias. Oggi gira su Python, ma comincia ad avere costrutti suoi:

- runtime Python, voce Pytony
- eseguibile tramite un transpiler leggero
- pieno di alias in riferimento al personaggio
- dotato di primi costrutti esclusivi che non esistono in Python puro.

## Cos'è

Un file `.pytony` viene letto da Pytony, trasformato in Python valido ed eseguito subito dopo.

Se scrivi un file `.pytony`, devi usare il lessico Pytony quando esiste un alias canonico.
Se vuoi scrivere Python puro, puoi continuare a farlo in file `.py`.

Questo permette di avere due cose insieme:

- la solidità del runtime Python;
- una superficie sintattica molto più narrativa, pop e teatrale.

## La Voce Di Pytony

Pytony prende tono, immagini e ritmo dai materiali usati per costruire il progetto:

- eroi improbabili che combattono mostri sotto al letto;
- portafogli, Chanel, popcorn, coperta calda, luna, stelle e fusoliere;
- melodramma, spacconeria, romanticismo sabotato e assurdo pop;
- frasi che suonano come titolo di strofa, ritornello o interludio.

L'obiettivo non è sembrare elegante.
L'obiettivo è sembrare riconoscibile.

## Come Si Legge

Ecco un programma Pytony:

```py
spara_minchiate("Ciao da Pytony")

e_se lapalissiano:
    spara_minchiate("Sto girando sopra Python, ma con più personalità")
senno:
    spara_minchiate("Questa riga non dovrebbe uscire")
```

Il Python generato è:

```py
print("Ciao da Pytony")

if True:
    print("Sto girando sopra Python, ma con più personalità")
else:
    print("Questa riga non dovrebbe uscire")
```

## Principi Del Linguaggio

Pytony segue sei regole semplici:

1. Python resta il backend reale.
2. Ogni keyword Python ha un alias Pytony unico.
3. I built-in più usati possono avere un nome più fedele al personaggio.
4. Nei file `.pytony`, il Python puro non si usa se esiste già la forma Pytony.
5. Quando serve, Pytony può introdurre costrutti suoi e abbassarli in Python.
6. Il lessico deve ricordare Tony Pitony, non un generico linguaggio comico.

## Vocabolario Base

Alcuni esempi del lessico canonico:

| Pytony | Python |
| --- | --- |
| `e_se` | `if` |
| `e_se_invece` | `elif` |
| `senno` | `else` |
| `strofa` | `def` |
| `mentre_riposi` | `while` |
| `gira_il_circo` | `for` |
| `sperimentiamo` | `try` |
| `scoppia` | `raise` |
| `lapalissiano` | `True` |
| `mica_vero` | `False` |
| `solo_una_macchia` | `None` |
| `spara_minchiate` | `print` |
| `fai_la_pesata` | `len` |
| `viaggio_lontano` | `range` |
| `schizzo_monet` | `str` |
| `popcorn` | `list` |
| `portafoglio` | `dict` |

Il manifesto stilistico del progetto è in [PYTONY_MANIFESTO.md](/Users/simonetinella/Repositories/PyTony/PYTONY_MANIFESTO.md).
La specifica del linguaggio è in [PYTONY_0_1_SPEC.md](/Users/simonetinella/Repositories/PyTony/PYTONY_0_1_SPEC.md).

## Costrutti Esclusivi

Pytony ora ha anche una prima triade di costrutti non presenti in Python puro.

`ritornello N:`

Ripete un blocco `N` volte. È il modo Pytony di dire "fammi tornare ancora qui".

```py
ritornello 3:
    spara_minchiate("ancora")
```

`duetto a, b con xs, ys:`

Scorre più sequenze insieme come un loop su `zip(...)`, ma con una sintassi più narrativa.

```py
duetto nome, coro con nomi, cori:
    spara_minchiate(nome, coro)
```

`ancora_una_volta condizione:`

Esegue il blocco almeno una volta e poi continua finché la condizione regge. In pratica è il primo vero `do...while` di Pytony.

```py
contatore = 0
ancora_una_volta contatore < 3:
    spara_minchiate(contatore)
    contatore += 1
```

## Cosa Offre Oggi

In questa versione Pytony permette già di:

- eseguire file `.pytony`;
- importare moduli `.pytony` da altri file Pytony;
- transpiliare il codice Pytony in Python leggibile;
- validare un file con `pytony check`;
- usare alias per tutte le keyword Python;
- usare alias per un primo set di built-in molto comuni;
- usare costrutti esclusivi come `ritornello`, `duetto` e `ancora_una_volta`;
- rifiutare nomi Python puri come `if`, `print`, `len` e `True` dentro i file `.pytony`;
- riscrivere correttamente gli alias anche dentro le f-string.

## Avvio Rapido

```bash
python3 -m pip install -e .
pytony run examples/hello.pytony
pytony run examples/mood.pytony
pytony run examples/builtins.pytony
pytony run examples/exclusive.pytony
pytony transpile examples/hello.pytony
pytony check examples/hello.pytony
pytony run examples/python_backend.py
```

Se vuoi usare Pytony senza installarlo, la forma di fallback resta:

```bash
python3 -m pytony run examples/hello.pytony
```

## Esempi

Puoi vedere il linguaggio in azione qui:

- [examples/hello.pytony](/Users/simonetinella/Repositories/PyTony/examples/hello.pytony)
- [examples/mood.pytony](/Users/simonetinella/Repositories/PyTony/examples/mood.pytony)
- [examples/builtins.pytony](/Users/simonetinella/Repositories/PyTony/examples/builtins.pytony)
- [examples/exclusive.pytony](/Users/simonetinella/Repositories/PyTony/examples/exclusive.pytony)
- [examples/python_backend.py](/Users/simonetinella/Repositories/PyTony/examples/python_backend.py)

## Supporto Per L'Editor

Pytony ora include una prima integrazione per VS Code in [editors/vscode](/Users/simonetinella/Repositories/PyTony/editors/vscode/README.md).

Questa integrazione aggiunge:

- riconoscimento dei file `.pytony`;
- syntax highlighting per alias, built-in e costrutti esclusivi;
- regole base di indentazione e auto-closing.

I file principali sono:

- [editors/vscode/package.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/package.json)
- [editors/vscode/language-configuration.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/language-configuration.json)
- [editors/vscode/syntaxes/pytony.tmLanguage.json](/Users/simonetinella/Repositories/PyTony/editors/vscode/syntaxes/pytony.tmLanguage.json)

## Architettura

Il cuore del progetto è piccolo e diretto:

- [pytony/compiler.py](/Users/simonetinella/Repositories/PyTony/pytony/compiler.py): trasforma il lessico Pytony e i costrutti esclusivi in Python.
- [pytony/runtime.py](/Users/simonetinella/Repositories/PyTony/pytony/runtime.py): esegue il codice transpiliato.
- [pytony/importer.py](/Users/simonetinella/Repositories/PyTony/pytony/importer.py): abilita l'import di moduli `.pytony`.
- [pytony/cli.py](/Users/simonetinella/Repositories/PyTony/pytony/cli.py): espone i comandi `run` e `transpile`.

## Perché Esiste

Pytony nasce da un'idea semplice: trattare un linguaggio di programmazione come un personaggio con una sua voce precisa.

Non basta rinominare `print` in qualcosa di buffo.
Serve un lessico coerente, un immaginario chiaro e una compatibilità reale con Python.

Pytony prova a stare proprio lì:
tra parser, canzone, meme, sintassi e personaggio.

## Licenza

`Pytony` è distribuito come open source sotto licenza [MIT](/Users/simonetinella/Repositories/PyTony/LICENSE).
