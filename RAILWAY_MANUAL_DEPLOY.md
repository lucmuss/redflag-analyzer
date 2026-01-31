# 🚂 Railway.app - Manuelles 1-Klick Deployment

## Das Problem
Ich habe **keinen Zugriff** auf deinen Railway Account. Nur DU kannst deployen.

## Die Lösung: GitHub Deploy (EINFACHSTE METHODE!)

### Schritt 1: GitHub Repo erstellen
```bash
cd /home/skymuss/projects/redflag-analyzer
git remote -v
# Wenn kein GitHub Remote:
git remote add origin https://github.com/DEIN-USERNAME/redflag-analyzer.git
git branch -M main
git push -u origin main
```

### Schritt 2: Railway GitHub Integration
1. Öffne: https://railway.app/dashboard
2. Klick: **"+ New Project"** → **"Deploy from GitHub"**
3. Autorisiere GitHub
4. Wähle: Dein `redflag-analyzer` Repo
5. Wähle Branch: `main`
6. Railway erstellt automatisch alle Services! 🎉

### Schritt 3: Environment Variables setzen
Nach dem ersten Deploy:
1. Railway Dashboard → Dein Projekt
2. Variables Tab → Diese hinzufügen:

```
SECRET_KEY=random-sehr-sicheres-passwort-min-50-zeichen
DEBUG=false
ALLOWED_HOSTS=*.railway.app
```

### Schritt 4: Fertig!
- Website live unter: `https://redflag-analyzer-xxx.railway.app`
- Weitere Änderungen? Einfach `git push` → Railway deployed automatisch! 🚀

---

## Alternative: Direkter CLI Deploy

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
railway login
cd /home/skymuss/projects/redflag-analyzer

# Projekt erstellen
railway init
# Wähle: Create new project

# Deployen
railway up
```

---

## 🤖 Nur für mich möglich: Automatische GitHub Actions

Falls du willst, habe ich auch eine GitHub Actions erstellt (`.github/workflows/railway-deploy.yml`) die bei jedem `git push` automatisch deployt - aber nur wenn du deine `RAILWAY_TOKEN` als GitHub Secret speicherst.

**Nicht nötig** - die manuelle GitHub Integration funktioniert schon!
