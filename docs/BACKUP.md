# BACKUP.md — Backup & Restore

---

## Supabase PostgreSQL

- Supabase Pro plan : backups automatiques quotidiens (7 jours de rétention)
- Free plan : pas de backup automatique → exporter manuellement via `pg_dump`
- Tables critiques : `personas` (difficile à recréer), `jobs` (historique), `assets` (références aux fichiers)

### Export manuel (si Free plan)
```bash
pg_dump $SUPABASE_DB_URL --data-only --table=personas --table=jobs --table=assets --table=batch_jobs > backup_$(date +%Y%m%d).sql
```

## Supabase Storage

- Pas de backup automatique natif
- Les vidéos finales sont le livrable — s'assurer de les télécharger régulièrement
- V2 : ajouter un sync vers un bucket S3 en backup

## Redis

- Redis sur Railway est éphémère (pas de persistence garantie)
- Ce n'est pas un problème : Redis sert uniquement de broker Celery, pas de stockage durable
- Si Redis restart : les jobs en cours failent, mais peuvent être relancés manuellement

## Procédure de restore

1. Recréer les tables Supabase via `MIGRATIONS.md`
2. Importer le backup SQL
3. Les fichiers Storage sont toujours là (Storage est indépendant de la DB)
4. Relancer les jobs failed si nécessaire

---

*Dernière mise à jour : mars 2026*
