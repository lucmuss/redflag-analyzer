# 🚀 Railway.app - Projekt erstellen & Deployment

## Fehler: "Available options can not be empty"

Das Problem: Du hast noch **kein Projekt im Railway Dashboard** erstellt.

---

## ✅ Lösung: Mit GitHub verbinden (EINFACHSTE METHODE!)

### Schritt 1: Repo auf GitHub pushen
```bash
cd /home/skymuss/projects/redflag-analyzer
git remote -v
# Wenn kein origin: git remote add origin https://github.com/dein-username/redflag-analyzer.git
git push origin main
```

### Schritt 2: Railway Dashboard
1. Öffne: https://railway.app/dashboard
2. Klick "New Project" → "Deploy from GitHub"
3. Authorisiere GitHub
4. Wähle: `redflag-analyzer` Repo
5. Wähle: `main` Branch
6. Fertig! Railway deployed automatisch! 🎉

---

## Alternative: Manuelles Projekt erstellen

```bash
export PATH="$HOME/.npm-global/bin:$PATH"

# 1. Öffne Dashboard & erstelle leeres Projekt manuell
# https://railway.app/dashboard → New Project → Empty Project

# 2. Dann CLI:
cd /home/skymuss/projects/redflag-analyzer
railway init
# Sollte jetzt dein Projekt in der Liste zeigen

railway up
```

---

## 💡 EMPFEHLUNG: 
**GitHub-Methode!** Railway deployed dann automatisch bei jedem `git push`
