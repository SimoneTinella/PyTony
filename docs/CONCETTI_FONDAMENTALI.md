# Concetti Fondamentali Di Pytony

Questa guida presenta i concetti principali del linguaggio in ordine didattico.

## 1. Stampare Un Messaggio

In `Pytony`, il modo canonico per mostrare qualcosa a schermo è:

```py
spara_minchiate("Ciao")
```

Equivalente Python:

```py
print("Ciao")
```

## 2. Valori Base

I tre valori linguistici fondamentali sono:

- `lapalissiano` per `True`
- `mica_vero` per `False`
- `solo_una_macchia` per `None`

Esempio:

```py
stato = lapalissiano
vuoto = solo_una_macchia
```

## 3. Variabili

Una variabile serve a conservare un valore.

```py
nome = "Tony"
eta = 27
spara_minchiate(nome)
```

## 4. Condizioni

Le condizioni permettono di decidere quale blocco eseguire.

```py
nome = "Pytony"

e_se nome == "Pytony":
    spara_minchiate("Presente")
senno:
    spara_minchiate("Assente")
```

## 5. Loop

### `mentre_riposi`

Serve a ripetere un blocco finché una condizione resta vera.

```py
contatore = 0
mentre_riposi contatore < 3:
    spara_minchiate(contatore)
    contatore += 1
```

### `gira_il_circo`

Serve a scorrere un insieme di valori.

```py
gira_il_circo numero nell_alta_marea viaggio_lontano(3):
    spara_minchiate(numero)
```

## 6. Collezioni

`Pytony` usa le strutture dati di Python con alias dedicati.

```py
nomi = popcorn(["Tony", "Pitony"])
rubrica = portafoglio({"voce": "alto"})
insieme = mostri({"dramma", "pop"})
```

I built-in più comuni sono:

- `popcorn` -> `list`
- `portafoglio` -> `dict`
- `mostri` -> `set`
- `coperta_calda` -> `tuple`

## 7. Funzioni

Le funzioni si definiscono con `strofa`.

```py
strofa saluta(nome):
    restero f"Ciao, {nome}"

spara_minchiate(saluta("Pytony"))
```

Una funzione:

- riceve input;
- esegue un blocco di codice;
- può restituire un valore con `restero`.

## 8. Errori

`Pytony` usa `sperimentiamo`, `ma_ehi` e `scoppia`.

```py
sperimentiamo:
    scoppia RuntimeError("Boom")
ma_ehi RuntimeError come_monet errore:
    spara_minchiate(errore)
```

Questo concetto serve a imparare la gestione controllata dei problemi nel programma.

## 9. Pattern Matching

`interludio` e `bridge` permettono di descrivere casi diversi in modo leggibile.

```py
interludio numero:
    bridge 1:
        spara_minchiate("uno")
    bridge oh_oh:
        spara_minchiate("altro")
```

## 10. Costrutti Esclusivi

`Pytony` introduce anche costrutti non presenti in Python puro.

### `ritornello`

```py
ritornello 3:
    spara_minchiate("ancora")
```

### `duetto`

```py
duetto nome, coro con nomi, cori:
    spara_minchiate(nome, coro)
```

### `ancora_una_volta`

```py
contatore = 0
ancora_una_volta contatore < 2:
    spara_minchiate(contatore)
    contatore += 1
```

## 11. Collegamento Con Python

Un punto didattico centrale di `Pytony` è questo:

- i concetti sono quelli della programmazione reale;
- la sintassi ha una voce più narrativa;
- il backend resta Python.

Quindi imparare `Pytony` può aiutare anche a capire meglio Python.
