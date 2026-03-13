# TESTS.md — Stratégie de Tests

---

## Stack de tests

- **Backend :** pytest + pytest-asyncio + httpx (test client FastAPI)
- **Frontend :** pas de tests automatisés en V1 (test manuel)
- **Mocks :** unittest.mock pour fal.ai, Supabase, yt-dlp

## Quoi tester

### Services (priorité haute)
- `fal_client.py` : mock les appels HTTP, tester le parsing des réponses, les timeouts, les retries
- `downloader.py` : mock yt-dlp subprocess, tester les erreurs (URL invalide, timeout, fichier trop gros)
- `overlay.py` : tester avec une vidéo de test réelle (fixture), vérifier que le MP4 output est valide
- `storage.py` : mock Supabase Storage, tester upload/download/delete

### Tasks (priorité moyenne)
- Tester que chaque task met à jour le job status correctement en DB
- Tester le comportement en cas d'erreur (retry vs fail)
- Tester la chain (pipeline_single) avec des mocks

### Routes API (priorité moyenne)
- Tester chaque endpoint avec httpx TestClient
- Tester les validations Pydantic (422 sur inputs invalides)
- Tester les 404, 409, 423

### Fixtures
- Persona de test (CherryPick avec des prompts courts)
- Vidéo trend de test (5s MP4, ~1Mo)
- Image de test (768x1344 PNG)
- Font de test (Bebas Neue TTF)

## Coverage
- Objectif V1 : 60%+ sur les services, 40%+ global
- Les mocks fal.ai sont critiques (on ne veut pas appeler l'API réelle en CI)

---

*Dernière mise à jour : mars 2026*
