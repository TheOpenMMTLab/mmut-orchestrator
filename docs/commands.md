# SHACL Validation Commands

Diese Beispiele gehen davon aus, dass das aktuelle Verzeichnis `docs/` ist.

## 1. Loop-Beispiel (sollte fehlschlagen)

```bash
pyshacl -s mmut-shapes.ttl ../tests/data/mmut/25350c66-f832-4c8d-b1cf-5b49e890806d/test-loop.ttl -f human
```

Erwartung: `Conforms: False`

## 2. Reales MMUT-Beispiel

```bash
pyshacl -s mmut-shapes.ttl ../mmut/574ae00d-db14-4e46-82db-c143aa8c1a0f/mmut-squirrl.ttl -f human
```

Tipp: Für ausführliche Diagnose kann `-d` ergänzt werden.
