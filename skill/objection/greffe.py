#!/usr/bin/env python3
"""Greffe du tribunal : tient proces.js à jour pendant l'audience, pour que la salle la suive en direct.

  greffe.py start "<affaire>" ["<pièce>" ...]     ouvre un procès et la salle dans le navigateur, la Défense est attendue
                                                  une pièce = un nom court, ou "Nom=https://lien" pour un artefact
  greffe.py add "<qui>" "<prochain orateur>"      ajoute la réplique lue sur stdin
  greffe.py add "<qui>"                           dernière réplique : clôt le procès
                                                  options de add, à la fin : --ms <durée> --outils <nombre d'actions>
  greffe.py end ko                                clôt un procès qui a échoué en route
  greffe.py fait 1 3                              coche dans la salle les étapes de la décision déjà appliquées
  greffe.py reglement                             affiche le chemin et le contenu du règlement du tribunal
"""
import json, pathlib, sys, time, webbrowser

ROOT = pathlib.Path(__file__).resolve().parents[2]  # racine du dépôt, même quand le skill est installé par lien symbolique
F = ROOT / 'proces.js'
REGLEMENT = ROOT / 'reglement.md'  # critères permanents de l'utilisateur, hors dépôt
PREFIX = 'window.TRIAL = '
ROLES = ('Défense', 'Accusation', 'Témoin', 'Jury', 'Juge')


def load():
    return json.loads(F.read_text(encoding='utf-8')[len(PREFIX):])


def save(trial):
    tmp = F.with_suffix('.tmp')  # écriture atomique : la page relit le fichier toutes les 1,5 s
    tmp.write_text(PREFIX + json.dumps(trial, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(F)


cmd, args = sys.argv[1], sys.argv[2:]
if cmd == 'start':
    save({'t': int(time.time() * 1000), 'q': args[0], 'done': False, 'next': ROLES[0], 'pieces': args[1:], 'log': []})
    webbrowser.open((ROOT / 'index.html').as_uri())
elif cmd == 'add':
    stats = {}
    while len(args) >= 2 and args[-2] in ('--ms', '--outils'):
        stats[{'--ms': 'ms', '--outils': 'tools'}[args[-2]]] = int(args[-1])
        args = args[:-2]
    who, nxt = args[0], (args[1] if len(args) > 1 else '')
    text = sys.stdin.read().strip()
    assert who.startswith(ROLES), f'« {who} » doit commencer par {ROLES}'
    assert not nxt or nxt in ROLES, f'prochain orateur inconnu : {nxt}'
    assert text, 'réplique vide sur stdin'
    trial = load()
    trial['log'].append({'who': who, 'text': text, **stats})
    if nxt:
        trial['next'] = nxt
    else:
        trial.pop('next', None)
        trial['done'] = True
    save(trial)
elif cmd == 'end':
    trial = load()
    trial.pop('next', None)
    trial['done'] = args[:1] != ['ko']
    save(trial)
elif cmd == 'fait':
    trial = load()
    trial['fait'] = sorted(set(trial.get('fait', [])) | {int(a) for a in args})
    save(trial)
elif cmd == 'reglement':
    print(f'FICHIER : {REGLEMENT}')
    print(REGLEMENT.read_text(encoding='utf-8').strip() if REGLEMENT.exists() else '(aucun règlement pour l\'instant)')
else:
    sys.exit(__doc__)
