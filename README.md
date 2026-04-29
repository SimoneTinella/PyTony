![Pytony](<pytony.png>)

# Pytony

Pytony e un linguaggio di programmazione costruito sopra Python, ma parlato come se Python fosse finito dentro una canzone di Tony Pitony.

Non e un linguaggio alternativo a Python. E Python con un'altra voce:

- totalmente compatibile con Python;
- eseguibile tramite un transpiler leggero;
- pieno di alias che arrivano dai testi in [testi canzoni](/Users/simonetinella/Repositories/PyTony/testi%20canzoni);
- pensato per trasformare la sintassi in un personaggio, non solo in una gag.

## Cos'e

Un file `.pytony` viene letto da Pytony, trasformato in Python valido ed eseguito subito dopo.

Se scrivi Python puro, continua a funzionare.
Se invece usi il lessico di Pytony, il compilatore lo riscrive nel Python equivalente.

Questo permette di avere due cose insieme:

- la solidita del runtime Python;
- una superficie sintattica molto piu narrativa, pop e teatrale.

## La Voce Di Pytony

Pytony prende tono, immagini e ritmo dai materiali usati per costruire il progetto:

- eroi improbabili che combattono mostri sotto al letto;
- portafogli, Chanel, popcorn, coperta calda, luna, stelle e fusoliere;
- melodramma, spacconeria, romanticismo sabotato e assurdo pop;
- frasi che suonano come titolo di strofa, ritornello o interludio.

L'obiettivo non e sembrare elegante.
L'obiettivo e sembrare riconoscibile.

## Come Si Legge

Ecco un programma Pytony:

```py
spara_minchiate("Ciao da Pytony")

e_se lapalissiano:
    spara_minchiate("Sto girando sopra Python, ma con piu personalita")
senno:
    spara_minchiate("Questa riga non dovrebbe uscire")
```

Il Python generato e:

```py
print("Ciao da Pytony")

if True:
    print("Sto girando sopra Python, ma con piu personalita")
else:
    print("Questa riga non dovrebbe uscire")
```

## Principi Del Linguaggio

Pytony segue quattro regole semplici:

1. Python resta il backend reale.
2. Ogni keyword Python ha un alias Pytony unico.
3. I built-in piu usati possono avere un nome piu fedele al personaggio.
4. Il lessico deve ricordare Tony Pitony, non un generico linguaggio comico.

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

Il manifesto stilistico del progetto e in [PYTONY_MANIFESTO.md](/Users/simonetinella/Repositories/PyTony/PYTONY_MANIFESTO.md).

## Cosa Offre Oggi

In questa versione Pytony permette gia di:

- eseguire file `.pytony`;
- transpiliare il codice Pytony in Python leggibile;
- usare alias per tutte le keyword Python;
- usare alias per un primo set di built-in molto comuni;
- riscrivere correttamente gli alias anche dentro le f-string.

## Avvio Rapido

```bash
python3 -m pytony run examples/hello.pytony
python3 -m pytony run examples/mood.pytony
python3 -m pytony run examples/builtins.pytony
python3 -m pytony transpile examples/hello.pytony
```

Se vuoi installare la CLI in locale:

```bash
pip install -e .
pytony run examples/hello.pytony
```

## Esempi

Puoi vedere il linguaggio in azione qui:

- [examples/hello.pytony](/Users/simonetinella/Repositories/PyTony/examples/hello.pytony)
- [examples/mood.pytony](/Users/simonetinella/Repositories/PyTony/examples/mood.pytony)
- [examples/builtins.pytony](/Users/simonetinella/Repositories/PyTony/examples/builtins.pytony)
- [examples/python_puro.pytony](/Users/simonetinella/Repositories/PyTony/examples/python_puro.pytony)

## Architettura

Il cuore del progetto e piccolo e diretto:

- [pytony/compiler.py](/Users/simonetinella/Repositories/PyTony/pytony/compiler.py): trasforma il lessico Pytony in Python.
- [pytony/runtime.py](/Users/simonetinella/Repositories/PyTony/pytony/runtime.py): esegue il codice transpiliato.
- [pytony/cli.py](/Users/simonetinella/Repositories/PyTony/pytony/cli.py): espone i comandi `run` e `transpile`.

## Perche Esiste

Pytony nasce da un'idea semplice: trattare un linguaggio di programmazione come un personaggio con una sua voce precisa.

Non basta rinominare `print` in qualcosa di buffo.
Serve un lessico coerente, un immaginario chiaro e una compatibilita reale con Python.

Pytony prova a stare proprio li:
tra parser, canzone, meme, sintassi e personaggio.
